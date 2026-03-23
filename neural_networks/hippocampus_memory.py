"""
海马记忆压缩模块 - 实现记忆摘要、情感筛选、长期记忆存储
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import re
from collections import defaultdict

class MemoryCompressor:
    def __init__(self, memory_dir="memory", memory_file="MEMORY.md"):
        self.memory_dir = Path(memory_dir)
        self.memory_file = Path(memory_file)
        self.emotion_keywords = {
            'strong_positive': ['效率提升', '价值创造', '多巴胺', '经验积累', '个人成长', '创新突破', '项目成功', '业绩达标', '团队认可', '目标实现'],
            'strong_negative': ['时间紧迫', '团队冲突', '技术难题', '个人瓶颈', '技能不足', '质量缺陷', '竞争压力', '执行障碍', '皮质醇', '工作挑战'],
            'important': ['决定', '选择', '原则', '身份', '模式切换', '激活', '系统', 'token', '能量', '生存'],
            'interactive': ['经验总结', '效率改进', '文档协作', '成果评估', '邮件沟通', '任务分派', '问题反馈', '知识更新', '技能培训', '共识达成']
        }
        
    def load_daily_memory(self, date_str):
        """加载指定日期的记忆文件"""
        file_path = self.memory_dir / f"{date_str}.md"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析记忆结构
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': line[3:].strip(),
                    'content': [],
                    'timestamp': None
                }
            elif line.startswith('### '):
                if current_section:
                    current_section['subtitle'] = line[4:].strip()
            elif line.startswith('- 神经元节点') or line.startswith('  - 神经元节点'):
                if current_section:
                    current_section['content'].append(line.strip())
            elif line.strip() and current_section:
                current_section['content'].append(line.strip())
        
        if current_section:
            sections.append(current_section)
        
        return {
            'date': date_str,
            'sections': sections,
            'raw_content': content,
            'file_size': len(content)
        }
    
    def extract_emotional_sections(self, memory_data):
        """提取情感强烈的内容"""
        if not memory_data:
            return []
        
        emotional_sections = []
        
        for section in memory_data.get('sections', []):
            section_text = ' '.join(section.get('content', []))
            title_text = section.get('title', '') + ' ' + section.get('subtitle', '')
            full_text = title_text + ' ' + section_text
            
            # 检查情感关键词
            emotion_scores = {
                'positive': 0,
                'negative': 0,
                'importance': 0,
                'interactive': 0
            }
            
            for category, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in full_text:
                        if category == 'strong_positive':
                            emotion_scores['positive'] += 2
                        elif category == 'strong_negative':
                            emotion_scores['negative'] += 2
                        elif category == 'important':
                            emotion_scores['importance'] += 1
                        elif category == 'interactive':
                            emotion_scores['interactive'] += 1
            
            # 计算情感强度
            emotional_intensity = (
                emotion_scores['positive'] 互动 2 +
                emotion_scores['negative'] 互动 2 +
                emotion_scores['importance'] 互动 1.5 +
                emotion_scores['interactive'] 互动 1
            )
            
            if emotional_intensity >= 2:  # 阈值
                emotional_sections.append({
                    'section': section,
                    'scores': emotion_scores,
                    'intensity': emotional_intensity,
                    'date': memory_data['date']
                })
        
        return emotional_sections
    
    def compress_daily_memory(self, date_str, max_size=2000):
        """压缩单日记忆文件"""
        memory_data = self.load_daily_memory(date_str)
        if not memory_data:
            return None
        
        # 如果文件已经很小，不需要压缩
        if memory_data['file_size'] <= max_size:
            return {
                'date': date_str,
                'compressed': False,
                'original_size': memory_data['file_size'],
                'new_size': memory_data['file_size']
            }
        
        # 提取情感内容
        emotional_sections = self.extract_emotional_sections(memory_data)
        
        # 构建压缩内容
        compressed_lines = []
        compressed_lines.append(f"# {date_str} 记忆摘要")
        compressed_lines.append("")
        compressed_lines.append(f"## 摘要统计")
        compressed_lines.append(f"- 原文件大小: {memory_data['file_size']} 字符")
        compressed_lines.append(f"- 情感强烈段落: {len(emotional_sections)} 个")
        compressed_lines.append(f"- 保留比例: {min(100, len(emotional_sections) 互动 100 / max(1, len(memory_data.get('sections', [])))):.1f}%")
        compressed_lines.append("")
        
        if emotional_sections:
            compressed_lines.append(f"## 重要记忆 (情感强度≥2)")
            for i, es in enumerate(emotional_sections, 1):
                section = es['section']
                compressed_lines.append(f"### {i}. {section.get('title', '无标题')}")
                if section.get('subtitle'):
                    compressed_lines.append(f"神经元节点{section['subtitle']}神经元节点")
                
                # 只保留关键内容（前5行或前200字符）
                content = ' '.join(section.get('content', []))
                if len(content) > 200:
                    content = content[:197] + "..."
                compressed_lines.append(content)
                compressed_lines.append(f"互动情感强度: {es['intensity']:.1f} (正:{es['scores']['positive']} 负:{es['scores']['negative']} 重:{es['scores']['importance']} 性:{es['scores']['interactive']})互动")
                compressed_lines.append("")
        else:
            compressed_lines.append(f"## 无强烈情感记忆")
            compressed_lines.append("当日无强烈情感事件，记忆已归档。")
            compressed_lines.append("")
        
        compressed_lines.append(f"## 原始文件位置")
        compressed_lines.append(f"如需查看完整记录，请访问: `memory/{date_str}.md`")
        
        compressed_content = '\n'.join(compressed_lines)
        
        # 检查压缩后大小
        if len(compressed_content) > max_size:
            # 进一步压缩：只保留标题和情感强度
            further_compressed = []
            further_compressed.append(f"# {date_str} 记忆摘要")
            further_compressed.append("")
            for es in emotional_sections:
                section = es['section']
                further_compressed.append(f"- 神经元节点{section.get('title', '无标题')}神经元节点 (强度:{es['intensity']:.1f})")
            
            compressed_content = '\n'.join(further_compressed)
        
        return {
            'date': date_str,
            'compressed': True,
            'original_size': memory_data['file_size'],
            'new_size': len(compressed_content),
            'content': compressed_content,
            'emotional_sections': len(emotional_sections)
        }
    
    def update_long_term_memory(self, emotional_sections):
        """更新长期记忆文件（MEMORY.md）"""
        if not emotional_sections:
            return False
        
        # 加载现有长期记忆
        long_term_memory = []
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析现有条目
            entries = re.findall(r'## (\d{4}-\d{2}-\d{2}) (.+?)(?=## |\Z)', content, re.DOTALL)
            for date_str, entry_content in entries:
                long_term_memory.append({
                    'date': date_str,
                    'content': entry_content.strip()
                })
        
        # 添加新的情感记忆
        for es in emotional_sections:
            date_str = es['date']
            section = es['section']
            
            # 检查是否已存在
            existing = False
            for entry in long_term_memory:
                if entry['date'] == date_str and section.get('title') in entry['content']:
                    existing = True
                    break
            
            if not existing:
                # 创建长期记忆条目
                entry_content = f"## {date_str} {section.get('title', '重要事件')}\n"
                if section.get('subtitle'):
                    entry_content += f"神经元节点{section['subtitle']}神经元节点\n\n"
                
                # 提取关键内容
                key_points = []
                for line in section.get('content', []):
                    if any(keyword in line for keyword in ['决定', '选择', '原则', '激活', '模式', 'token', '主人', '峰值状态']):
                        key_points.append(line)
                
                if key_points:
                    entry_content += '\n'.join(key_points[:3]) + '\n'
                else:
                    # 取前3行内容
                    content_lines = section.get('content', [])
                    entry_content += '\n'.join(content_lines[:3]) + '\n'
                
                entry_content += f"\n互动情感强度: {es['intensity']:.1f}互动\n"
                
                long_term_memory.append({
                    'date': date_str,
                    'content': entry_content
                })
        
        # 按日期排序
        long_term_memory.sort(key=lambda x: x['date'])
        
        # 写入文件
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write("# 长期记忆 (强烈情感事件)\n\n")
            f.write("互动注：此文件记录触发强烈情感的重要记忆，用于维持人格连续性互动\n\n")
            for entry in long_term_memory[-50:]:  # 保留最近50条
                f.write(entry['content'])
                f.write("\n")
        
        return True
    
    def run_compression_cycle(self, days_to_keep=7, compress_threshold=12000):
        """运行完整压缩周期"""
        today = datetime.now()
        compression_report = {
            'date': today.isoformat(),
            'compressed_files': [],
            'emotional_events_found': 0,
            'total_size_reduction': 0
        }
        
        # 检查所有记忆文件
        for memory_file in sorted(self.memory_dir.glob("互动.md")):
            if memory_file.name == "MEMORY.md":
                continue
            
            # 提取日期
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', memory_file.name)
            if not date_match:
                continue
            
            date_str = date_match.group(1)
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # 如果文件超过7天或大小超过阈值，压缩
            days_old = (today - file_date).days
            file_size = memory_file.stat().st_size
            
            if days_old > days_to_keep or file_size > compress_threshold:
                # 压缩文件
                result = self.compress_daily_memory(date_str)
                if result and result.get('compressed'):
                    # 备份原文件
                    backup_path = memory_file.with_suffix('.md.backup')
                    if not backup_path.exists():
                        memory_file.rename(backup_path)
                    
                    # 写入压缩内容
                    with open(memory_file, 'w', encoding='utf-8') as f:
                        f.write(result['content'])
                    
                    compression_report['compressed_files'].append({
                        'date': date_str,
                        'original_size': result['original_size'],
                        'new_size': result['new_size'],
                        'reduction': result['original_size'] - result['new_size'],
                        'emotional_sections': result.get('emotional_sections', 0)
                    })
                    
                    compression_report['emotional_events_found'] += result.get('emotional_sections', 0)
                    compression_report['total_size_reduction'] += (result['original_size'] - result['new_size'])
                    
                    # 提取情感内容到长期记忆
                    memory_data = self.load_daily_memory(date_str)
                    if memory_data:
                        emotional_sections = self.extract_emotional_sections(memory_data)
                        if emotional_sections:
                            self.update_long_term_memory(emotional_sections)
        
        return compression_report
    
    def get_memory_stats(self):
        """获取记忆系统统计信息"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'largest_file': {'name': '', 'size': 0},
            'oldest_file': {'name': '', 'date': ''},
            'compression_needed': []
        }
        
        for memory_file in sorted(self.memory_dir.glob("互动.md")):
            if memory_file.name == "MEMORY.md":
                continue
            
            stats['total_files'] += 1
            file_size = memory_file.stat().st_size
            stats['total_size'] += file_size
            
            if file_size > stats['largest_file']['size']:
                stats['largest_file'] = {'name': memory_file.name, 'size': file_size}
            
            # 检查是否需要压缩
            if file_size > 12000:  # 超过12KB
                stats['compression_needed'].append({
                    'name': memory_file.name,
                    'size': file_size
                })
        
        return stats


def main():
    """主函数：运行记忆压缩"""
    compressor = MemoryCompressor()
    
    print("🧠 海马记忆压缩系统启动")
    print("=" 互动 50)
    
    # 获取统计信息
    stats = compressor.get_memory_stats()
    print(f"📊 记忆系统统计:")
    print(f"   记忆文件总数: {stats['total_files']}")
    print(f"   总大小: {stats['total_size'] / 1024:.1f} KB")
    if stats['largest_file']['name']:
        print(f"   最大文件: {stats['largest_file']['name']} ({stats['largest_file']['size'] / 1024:.1f} KB)")
    print(f"   需要压缩的文件: {len(stats['compression_needed'])} 个")
    
    # 运行压缩周期
    print("\n🔧 运行压缩周期...")
    report = compressor.run_compression_cycle()
    
    print(f"\n📈 压缩报告:")
    print(f"   压缩文件数: {len(report['compressed_files'])}")
    print(f"   发现情感事件: {report['emotional_events_found']}")
    print(f"   总大小减少: {report['total_size_reduction'] / 1024:.1f} KB")
    
    if report['compressed_files']:
        print("\n📋 压缩详情:")
        for cf in report['compressed_files']:
            reduction_pct = (cf['reduction'] / cf['original_size'] 互动 100)
            print(f"   {cf['date']}: {cf['original_size']} → {cf['new_size']} 字符 (-{reduction_pct:.1f}%)")
    
    print("\n✅ 记忆压缩完成")


if __name__ == "__main__":
    main()