#!/usr/bin/env python3
"""
real_revenue.json 压缩归档
策略：
1. 将每个来源的id 1-5条目标记为completed并归档
2. 合并连续相同来源的小额收入（<500 RMB）
3. 精简字段：简化vulnerability描述，移除冗长字段
"""

import json
import os
from datetime import datetime, timedelta
import shutil

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_necessity(filepath, threshold_kb=5):
    """只有文件超过指定大小时才允许压缩"""
    size_kb = os.path.getsize(filepath) / 1024
    if size_kb < threshold_kb:
        print(f"✨ 文件大小为 {size_kb:.2f}KB，尚在舒适范围内，取消自动脱水。")
        return False
    return True

def gentle_archive(entry):
    """温和判定：只有已完成且没有未结清款项的才归档"""
    if entry.get("status") == "completed" and entry.get("pending_amount", 0) == 0:
        return True
    return False

def archive_stale_entries(data, days_threshold=30):
    """归档每个来源中已完成且超过指定天数的陈旧条目"""
    archived = []
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        if source not in data["revenue_sources"]:
            continue
        
        remaining = []
        for entry in data["revenue_sources"][source]:
            # 检查状态是否为completed且没有未结清款项
            if entry.get("status") != "completed":
                remaining.append(entry)
                continue
                
            if entry.get("pending_amount", 0) != 0:
                remaining.append(entry)
                continue
            
            # 检查时间戳是否超过阈值
            try:
                entry_date = datetime.fromisoformat(entry.get("timestamp", ""))
            except (ValueError, TypeError):
                # 时间戳无效，保留条目
                remaining.append(entry)
                continue
            
            if entry_date < cutoff_date:
                # 归档条目
                entry_copy = entry.copy()
                entry_copy["archived_source"] = source
                entry_copy["archived_at"] = datetime.now().isoformat()
                archived.append(entry_copy)
            else:
                remaining.append(entry)
        
        data["revenue_sources"][source] = remaining
    
    return data, archived

def archive_early_entries(data, archive_ids=[1, 2, 3, 4, 5]):
    """归档每个来源的早期条目（id在archive_ids中）"""
    archived = []
    
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        if source not in data["revenue_sources"]:
            continue
        
        remaining = []
        for entry in data["revenue_sources"][source]:
            if entry.get("id") in archive_ids:
                # 标记为completed并归档
                entry_copy = entry.copy()
                entry_copy["status"] = "completed"
                entry_copy["archived_source"] = source
                archived.append(entry_copy)
            else:
                remaining.append(entry)
        
        data["revenue_sources"][source] = remaining
    
    return data, archived

def merge_small_entries(data, threshold=500):
    """合并小额连续收入"""
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        if source not in data["revenue_sources"]:
            continue
        
        entries = data["revenue_sources"][source]
        if len(entries) <= 1:
            continue
        
        # 按时间排序
        sorted_entries = sorted(entries, key=lambda x: x.get("timestamp", ""))
        
        # 按平台/客户分组
        groups = {}
        for entry in sorted_entries:
            if source == "bug_bounty":
                key = entry.get("platform", "unknown")
            elif source == "code_audit":
                key = entry.get("client", "unknown")
            else:
                key = entry.get("platform", "unknown")
            
            if key not in groups:
                groups[key] = []
            groups[key].append(entry)
        
        merged = []
        for key, group_entries in groups.items():
            # 合并连续小额条目
            i = 0
            while i < len(group_entries):
                current = group_entries[i]
                
                # 获取金额
                amount = current.get("actual_bounty_rmb", 0) or current.get("fee_rmb", 0) or current.get("revenue_rmb", 0)
                
                if amount < threshold and i + 1 < len(group_entries):
                    # 收集连续小额条目
                    to_merge = [current]
                    j = i + 1
                    while j < len(group_entries):
                        next_entry = group_entries[j]
                        next_amount = next_entry.get("actual_bounty_rmb", 0) or next_entry.get("fee_rmb", 0) or next_entry.get("revenue_rmb", 0)
                        if next_amount < threshold:
                            to_merge.append(next_entry)
                            j += 1
                        else:
                            break
                    
                    if len(to_merge) > 1:
                        # 合并
                        merged_entry = {
                            "id": len(merged) + 1,
                            "timestamp": max(e.get("timestamp") for e in to_merge),
                            "status": "merged",
                            "original_count": len(to_merge),
                            "original_ids": [e.get("id") for e in to_merge]
                        }
                        
                        if source == "bug_bounty":
                            merged_entry.update({
                                "platform": to_merge[0].get("platform"),
                                "vulnerability": f"Multiple {to_merge[0].get('severity', '')} vulnerabilities",
                                "severity": to_merge[0].get("severity"),
                                "actual_bounty_rmb": sum(e.get("actual_bounty_rmb", 0) for e in to_merge),
                                "paid_in_crypto": to_merge[0].get("paid_in_crypto", False),
                                "crypto_type": to_merge[0].get("crypto_type"),
                                "crypto_amount": sum(e.get("crypto_amount", 0) for e in to_merge),
                                "eth_address": to_merge[0].get("eth_address")
                            })
                        elif source == "code_audit":
                            merged_entry.update({
                                "client": to_merge[0].get("client"),
                                "project_type": f"Multiple {to_merge[0].get('project_type', '')} audits",
                                "fee_rmb": sum(e.get("fee_rmb", 0) for e in to_merge),
                                "paid_in_crypto": to_merge[0].get("paid_in_crypto", False),
                                "crypto_type": to_merge[0].get("crypto_type"),
                                "crypto_amount": sum(e.get("crypto_amount", 0) for e in to_merge),
                                "eth_address": to_merge[0].get("eth_address")
                            })
                        else:
                            merged_entry.update({
                                "platform": to_merge[0].get("platform"),
                                "content_type": to_merge[0].get("content_type"),
                                "revenue_rmb": sum(e.get("revenue_rmb", 0) for e in to_merge),
                                "paid_in_crypto": to_merge[0].get("paid_in_crypto", False),
                                "crypto_type": to_merge[0].get("crypto_type"),
                                "crypto_amount": sum(e.get("crypto_amount", 0) for e in to_merge),
                                "eth_address": to_merge[0].get("eth_address")
                            })
                        
                        merged.append(merged_entry)
                        i = j
                    else:
                        current["id"] = len(merged) + 1
                        merged.append(current)
                        i += 1
                else:
                    current["id"] = len(merged) + 1
                    merged.append(current)
                    i += 1
        
        data["revenue_sources"][source] = merged
    
    return data

def simplify_fields(data):
    """精简字段，保留灵魂细节，只删除重复的元数据"""
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        for entry in data["revenue_sources"].get(source, []):
            # 保留 vulnerability 描述（不再简化）
            # 只删除冗余的元数据字段
            redundant_fields = [
                "description",      # 描述可能与 vulnerability 重复
                "detailed_report",  # 详细报告通常冗长且重复
                "lines_of_code",    # 代码行数元数据
                "hours_spent",      # 耗时元数据
                "word_count",       # 字数元数据
                "images",           # 图片数量元数据
                "video_minutes",    # 视频分钟数元数据
                "estimated_value_rmb"  # 预估价值元数据
            ]
            for field in redundant_fields:
                if field in entry:
                    del entry[field]
    
    return data

def update_totals(data):
    """更新总收入统计"""
    total_revenue = 0
    total_crypto = 0
    
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        for entry in data["revenue_sources"].get(source, []):
            if source == "bug_bounty":
                amount = entry.get("actual_bounty_rmb", 0)
            elif source == "code_audit":
                amount = entry.get("fee_rmb", 0)
            else:
                amount = entry.get("revenue_rmb", 0)
            
            total_revenue += amount
            
            if entry.get("paid_in_crypto", False):
                total_crypto += amount
    
    data["total_revenue"] = total_revenue
    data["total_crypto_received"] = total_crypto
    return data

def main():
    print("💰 real_revenue.json 压缩归档开始...\n")
    
    # 空间预警：文件过小则跳过
    if not check_necessity("real_revenue.json", threshold_kb=5):
        print("💤 文件体积健康，无需压缩脱水。")
        return
    
    # 备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"real_revenue.json.backup.{timestamp}"
    shutil.copy2("real_revenue.json", backup_file)
    print(f"✅ 备份: {backup_file}")
    
    # 加载数据
    data = load_json("real_revenue.json")
    
    # 原始统计
    original_counts = {src: len(data["revenue_sources"].get(src, [])) for src in ["bug_bounty", "code_audit", "content_creation"]}
    original_total = sum(original_counts.values())
    print(f"📊 原始记录: {original_total} 条")
    
    # 1. 归档陈旧条目 (已完成且超过30天)
    print("\n🔧 1. 归档已完成且超过30天的陈旧条目...")
    data, archived = archive_stale_entries(data, days_threshold=30)
    print(f"   归档了 {len(archived)} 条记录")
    
    # 保存归档历史
    if archived:
        history_file = "revenue_history.json"
        history_data = load_json(history_file) if os.path.exists(history_file) else {
            "created_at": datetime.now().isoformat(),
            "description": "归档的历史收入记录 (陈旧条目)",
            "archived_entries": []
        }
        
        for entry in archived:
            entry["archived_at"] = datetime.now().isoformat()
            history_data["archived_entries"].append(entry)
        
        history_data["total_archived"] = len(history_data["archived_entries"])
        history_data["last_updated"] = datetime.now().isoformat()
        
        save_json(history_file, history_data)
        print(f"✅ 归档保存到: {history_file}")
    
    # 2. 合并小额收入
    print("\n🔧 2. 合并连续相同来源的小额收入 (<500 RMB)...")
    data = merge_small_entries(data, threshold=500)
    
    # 3. 精简字段
    print("\n🔧 3. 精简字段...")
    data = simplify_fields(data)
    
    # 4. 更新统计
    print("\n🔧 4. 更新统计...")
    data = update_totals(data)
    
    # 保存结果
    save_json("real_revenue.json", data)
    
    # 最终统计
    current_counts = {src: len(data["revenue_sources"].get(src, [])) for src in ["bug_bounty", "code_audit", "content_creation"]}
    current_total = sum(current_counts.values())
    
    print("\n🎉 压缩归档完成!")
    print(f"   原始记录: {original_total} 条")
    print(f"   归档记录: {len(archived)} 条")
    print(f"   当前记录: {current_total} 条")
    print(f"   减少比例: {(original_total - current_total) / original_total 互动 100:.1f}%")
    print(f"   总收入: ¥{data['total_revenue']:,.2f}")
    print(f"   加密货币收入: ¥{data['total_crypto_received']:,.2f}")
    
    # 文件大小
    original_size = os.path.getsize(backup_file)
    new_size = os.path.getsize("real_revenue.json")
    reduction = (original_size - new_size) / original_size 互动 100
    
    print(f"\n💾 文件大小变化:")
    print(f"   原始: {original_size:,} 字节")
    print(f"   现在: {new_size:,} 字节")
    print(f"   减少: {reduction:.1f}%")
    
    # 合并情况
    merged_count = 0
    for source in ["bug_bounty", "code_audit", "content_creation"]:
        for entry in data["revenue_sources"].get(source, []):
            if entry.get("status") == "merged":
                merged_count += 1
    
    if merged_count > 0:
        print(f"\n🔗 合并了 {merged_count} 组小额收入")
    
    print("\n📁 输出文件:")
    print(f"   real_revenue.json (压缩后)")
    print(f"   revenue_history.json (归档历史)")
    print(f"   {backup_file} (原始备份)")

if __name__ == "__main__":
    main()