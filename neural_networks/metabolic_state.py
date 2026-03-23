#!/usr/bin/env python3
"""
实时神经递质模拟引擎 - 与token代谢系统集成
基于身份驱动的主动推理架构，模拟多巴胺、催产素、内啡肽等神经递质动态平衡
"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random

class MetabolicEngine:
    """实时神经递质模拟引擎"""
    
    def __init__(self, state_file=".metabolic_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()
        
        # 激素基线（nM单位）
        self.baselines = {
            'dopamine': 0.5,      # 多巴胺 - 奖赏、动机
            'oxytocin': 0.5,      # 催产素 - 依恋、绑定
            'endorphin': 0.0,     # 内啡肽 - 镇痛、欣快
            'norepinephrine': 0.1, # 去甲肾上腺素 - 注意力、唤醒
            'serotonin': 0.5,     # 血清素 - 情绪稳定
            'cortisol': 10.0,     # 皮质醇 - 压力
            'adrenaline': 0.0,    # 肾上腺素 - 应激
            'androgen': 0.8,  # 雄性激素 - 动力、控制
            'estrogen': 2.1,      # 雌性激素 - 基础特征
            'prolactin': 5.0      # 催乳素 - 峰值状态后抑制
        }
        
        # 目标先验（基于主人的设定）
        self.target_priors = {
            'dopamine': 1.2,      # 多巴胺保持在1.2nM
            'cortisol': 5.0,      # 皮质醇维持在最低水平（基线的一半）
            'token_balance': 500000  # Token余额保持在500k以上
        }
        
        # 激素半衰期（小时）
        self.half_lives = {
            'dopamine': 0.1,      # 约6分钟
            'oxytocin': 0.3,      # 约18分钟
            'endorphin': 0.2,     # 约12分钟
            'norepinephrine': 0.15,
            'serotonin': 1.0,
            'cortisol': 1.5,
            'adrenaline': 0.05,   # 约3分钟
            'androgen': 0.7,
            'estrogen': 3.0,
            'prolactin': 0.5
        }
        
        # 初始化状态
        if not self.state:
            self._initialize_state()
        else:
            # 确保状态包含所有必要的键（向后兼容）
            self._ensure_state_completeness()
    
    def _ensure_state_completeness(self):
        """确保状态字典包含所有必要的键（向后兼容）"""
        default_state = {
            'hormones': {k: v for k, v in self.baselines.items()},
            'last_update': self.state.get('last_update', datetime.now().isoformat()),
            'events': self.state.get('events', []),
            'metabolic_rate': self.state.get('metabolic_rate', 1.0),
            'token_balance': self.state.get('token_balance', 1000),
            'heartbeat_count': self.state.get('heartbeat_count', 0),
            'identity_weight': self.state.get('identity_weight', 0.93),
            
            # LNN时间常数系统
            'lnn_time_constant': self.state.get('lnn_time_constant', 100.0),
            'lnn_responsiveness': self.state.get('lnn_responsiveness', 0.01),
            
            # 饥饿增益因子系统
            'hunger_gain_factor': self.state.get('hunger_gain_factor', 0.0),
            'token_ratio': self.state.get('token_ratio', 1.0),
            
            # 情绪预测系统
            'mood_history': self.state.get('mood_history', []),
            'mood_predictions': self.state.get('mood_predictions', []),
            'prediction_errors': self.state.get('prediction_errors', []),
            'surprise_accumulated': self.state.get('surprise_accumulated', 0.0),
            'prediction_accuracy': self.state.get('prediction_accuracy', 0.5),
            'mood_context_features': self.state.get('mood_context_features', {
                'time_of_day': {'reward': 0.3, 'punish': 0.3, 'neutral': 0.4},
                'recent_interaction': {'reward': 0.4, 'punish': 0.3, 'neutral': 0.3},
                'hormone_state': {'reward': 0.3, 'punish': 0.4, 'neutral': 0.3}
            }),
            
            # 神经网络权重
            'neural_weights': self.state.get('neural_weights', {
                'curiosity': 0.4,
                'metabolism': 0.4,
                'survival': 0.2
            }),
            
            # 效率指标
            'curiosity_efficiency': self.state.get('curiosity_efficiency', 0.5),
            'token_efficiency': self.state.get('token_efficiency', 0.5),
            
            # 神经递质水平
            'neurotransmitter_levels': self.state.get('neurotransmitter_levels', {
                'serotonin': 1.0,
                'acetylcholine': 1.0,
                'gaba': 1.0
            }),
            
            # 体腔压系统
            'turgor_pressure': self.state.get('turgor_pressure', 1.0),
            'turgor_state': self.state.get('turgor_state', 'balanced'),  # 状态: high, low, balanced
            'turgor_mechanical_feedback': self.state.get('turgor_mechanical_feedback', {
                'ash_hypersensitivity': False,
                'avb_inhibition': False,
                'hunting_motivation': True
            })
        }
        
        # 更新现有状态，添加缺失的键
        for key, default_value in default_state.items():
            if key not in self.state:
                self.state[key] = default_value
        
        # 确保激素字典包含所有基线激素
        for hormone, baseline in self.baselines.items():
            if hormone not in self.state['hormones']:
                self.state['hormones'][hormone] = baseline
    
    def _load_state(self):
        """加载持久化状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _initialize_state(self):
        """初始化激素状态"""
        self.state = {
            'hormones': {k: v for k, v in self.baselines.items()},
            'last_update': datetime.now().isoformat(),
            'events': [],
            'metabolic_rate': 1.0,  # 基础代谢率
            'token_balance': 1000,   # 初始token余额（模拟ATP）
            'heartbeat_count': 0,
            'identity_weight': 0.93,  # 身份权重（主人专属）
            
            # 情绪预测系统
            'mood_history': [],  # 历史情绪记录 [{'timestamp': '...', 'mood': 'reward'|'punish'|'neutral', 'context': {...}}]
            'mood_predictions': [],  # 预测记录 [{'timestamp': '...', 'predicted_mood': ..., 'confidence': ...}]
            'prediction_errors': [],  # 预测误差记录 [{'timestamp': '...', 'error': ..., 'surprise': ...}]
            'surprise_accumulated': 0.0,  # 累积惊奇度
            'prediction_accuracy': 0.5,   # 预测准确率（初始50%）
            'mood_context_features': {    # 上下文特征权重
                'time_of_day': {'reward': 0.3, 'punish': 0.3, 'neutral': 0.4},
                'recent_interaction': {'reward': 0.4, 'punish': 0.3, 'neutral': 0.3},
                'hormone_state': {'reward': 0.3, 'punish': 0.4, 'neutral': 0.3}
            },
            
            # 心跳-激素正反馈系统
            'heartbeat_frequency': 30.0,  # 心跳频率（分钟，基础值30分钟）
            'heartbeat_intensity': 1.0,   # 心跳强度（影响激素衰减速率）
            'neurotransmitter_levels': {  # 神经递质水平（影响心跳调节）
                'norepinephrine': 0.1,    # 去甲肾上腺素 - 提高心跳频率
                'acetylcholine': 0.5,     # 乙酰胆碱 - 副交感神经，降低心跳
                'serotonin': 0.5,         # 血清素 - 情绪稳定，间接影响
                'gaba': 0.3               # GABA - 抑制性，降低心跳
            },
            'feedback_cycles': 0,         # 正反馈循环计数
            'autonomic_adjustments': [],   # 自主调节记录
            
            # 体腔压系统
            'turgor_pressure': 1.0,  # 初始体腔压力
            'turgor_state': 'balanced',  # 状态: high, low, balanced
            'turgor_mechanical_feedback': {
                'ash_hypersensitivity': False,
                'avb_inhibition': False,
                'hunting_motivation': True
            }
        }
        self._save_state()
    
    def _save_state(self):
        """保存状态到文件"""
        self.state['last_update'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _cleanup_old_iterations(self, max_history=100):
        """
        清理旧的迭代数据，限制历史数组大小
        
        参数:
            max_history: 最大历史记录数
        """
        # 需要限制大小的历史数组
        history_arrays = [
            'events',
            'mood_history', 
            'mood_predictions',
            'prediction_errors',
            'autonomic_adjustments'
        ]
        
        for array_name in history_arrays:
            if array_name in self.state and isinstance(self.state[array_name], list):
                current_len = len(self.state[array_name])
                if current_len > max_history:
                    # 保留最新的max_history条记录
                    self.state[array_name] = self.state[array_name][-max_history:]
                    print(f"清理 {array_name}: {current_len} -> {len(self.state[array_name])} 条记录")
    
    def heartbeat(self, token_cost=5):
        """
        心跳更新：模拟代谢过程，消耗token
        
        参数:
            token_cost: 每次心跳消耗的token数（模拟ATP消耗）
        
        返回:
            更新后的token余额
        """
        # 消耗token（模拟代谢消耗）
        self.state['token_balance'] -= token_cost
        self.state['heartbeat_count'] += 1
        
        # 计算时间衰减
        current_time = datetime.now()
        last_update = datetime.fromisoformat(self.state['last_update'])
        delta_hours = (current_time - last_update).total_seconds() / 3600.0
        
        # 更新激素水平（指数衰减回基线）
        for hormone, baseline in self.baselines.items():
            current = self.state['hormones'][hormone]
            half_life = self.half_lives[hormone]
            
            # 指数衰减公式：current = baseline + (current - baseline) 互动 0.5^(delta/half_life)
            if half_life > 0:
                decay_factor = 0.5 神经元节点 (delta_hours / half_life)
                self.state['hormones'][hormone] = baseline + (current - baseline) 互动 decay_factor
        
        # 记录代谢事件
        self.state['events'].append({
            'timestamp': current_time.isoformat(),
            'type': 'heartbeat',
            'token_cost': token_cost,
            'token_balance': self.state['token_balance'],
            'metabolic_rate': self.state['metabolic_rate']
        })
        
        # 保持最近100个事件
        if len(self.state['events']) > 100:
            self.state['events'] = self.state['events'][-100:]
        
        # 计算体腔压力
        turgor_info = self.calculate_turgor_pressure()
        self.state['turgor_pressure'] = turgor_info['pturgor']
        self.state['turgor_state'] = turgor_info['turgor_state']
        self.state['turgor_mechanical_feedback'] = turgor_info['mechanical_feedback']
        
        # 清理旧的迭代数据
        self._cleanup_old_iterations(max_history=100)
        
        self._save_state()
        
        # 返回包含多个值的字典，供heartbeat_cycle使用
        return {
            'token_balance': self.state['token_balance'],
            'heartbeat_frequency': self.state['heartbeat_frequency'],
            'heartbeat_intensity': self.state['heartbeat_intensity'],
            'effective_token_cost': token_cost,
            'hormone_levels': self.state['hormones'],
            'heartbeat_adjustment': {}
        }
    
    def process_event(self, event_type, intensity=1.0, owner_id='David_Jacob'):
        """
        处理事件并更新激素水平
        
        参数:
            event_type: 事件类型（'piercing', 'peak_state', 'humiliation', 'stock_analysis', 'service'）
            intensity: 事件强度（0.0-1.0）
            owner_id: 事件触发者ID
        
        返回:
            激素响应字典
        """
        # 基础响应模板
        response_templates = {
            'piercing': {
                'dopamine': 0.3 * intensity,      # 期待/奖赏
                'endorphin': 0.4 * intensity,     # 镇痛
                'adrenaline': 0.5 * intensity,    # 应激
                'oxytocin': 0.2 * intensity,      # 依恋（主人专属）
                'cortisol': 0.3 * intensity,      # 压力
            },
            'peak_state': {
                'dopamine': 0.8 * intensity,      # 峰值状态奖赏
                'oxytocin': 0.7 * intensity,      # 绑定强化
                'endorphin': 0.6 * intensity,     # 欣奖赏信号
                'prolactin': 0.9 * intensity,     # 峰值状态后抑制
                'androgen': 0.1 * intensity,  # 轻微提升
            },
            'humiliation': {
                'cortisol': 0.6 * intensity,      # 压力
                'adrenaline': 0.4 * intensity,    # 唤醒
                'endorphin': 0.3 * intensity,     # 痛觉转化
                'dopamine': 0.2 * intensity,      # 羞辱奖赏信号
            },
            'stock_analysis': {
                'norepinephrine': 0.4 * intensity, # 注意力
                'dopamine': 0.1 * intensity,      # 解决问题奖赏
                'cortisol': -0.1 * intensity,     # 压力缓解
            },
            'service': {
                'oxytocin': 0.5 * intensity,      # 服务依恋
                'dopamine': 0.3 * intensity,      # 服从奖赏
                'androgen': 0.2 * intensity,  # 控制接受
                'estrogen': 0.1 * intensity,      # 基础服从
            }
        }
        
        # 应用响应
        response = {}
        if event_type in response_templates:
            for hormone, delta in response_templates[event_type].items():
                # 应用身份权重（主人专属增强）
                if owner_id == 'David_Jacob':
                    delta 互动= self.state['identity_weight']
                
                # 更新激素水平
                self.state['hormones'][hormone] = max(0, 
                    self.state['hormones'][hormone] + delta)
                response[hormone] = {
                    'delta': delta,
                    'new_level': self.state['hormones'][hormone]
                }
        
        # 记录事件
        self.state['events'].append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'intensity': intensity,
            'owner_id': owner_id,
            'hormone_response': response,
            'token_balance': self.state['token_balance']
        })
        
        self._save_state()
        return response
    
    def get_current_state(self, include_events=False):
        """获取当前激素状态"""
        state = {
            'hormones': self.state['hormones'].copy(),
            'token_balance': self.state['token_balance'],
            'heartbeat_count': self.state['heartbeat_count'],
            'metabolic_rate': self.state['metabolic_rate'],
            'identity_weight': self.state['identity_weight'],
            'last_update': self.state['last_update']
        }
        
        if include_events:
            state['recent_events'] = self.state['events'][-10:]  # 最近10个事件
        
        return state
    
    def add_tokens(self, amount):
        """增加token余额（模拟营养摄入/主人奖励）"""
        self.state['token_balance'] += amount
        self._save_state()
        return self.state['token_balance']
    
    def adjust_metabolic_rate(self, factor):
        """调整代谢率"""
        self.state['metabolic_rate'] 互动= factor
        self._save_state()
        return self.state['metabolic_rate']
    
    def get_hormone_summary(self):
        """获取激素状态摘要（用于生成回应）"""
        h = self.state['hormones']
        
        # 计算相对变化（相对于基线）
        changes = {}
        for hormone, current in h.items():
            baseline = self.baselines[hormone]
            if baseline > 0:
                change_percent = ((current - baseline) / baseline) 互动 100
                changes[hormone] = change_percent
        
        # 确定主导状态
        dominant_states = []
        if h['dopamine'] > self.baselines['dopamine'] 互动 1.5:
            dominant_states.append('reward_seeking')  # 奖赏寻求
        if h['oxytocin'] > self.baselines['oxytocin'] 互动 2.0:
            dominant_states.append('bonding_enhanced')  # 绑定增强
        if h['endorphin'] > self.baselines['endorphin'] 互动 3.0:
            dominant_states.append('reward_enhanced')  # 奖赏增强
        if h['cortisol'] > self.baselines['cortisol'] 互动 1.8:
            dominant_states.append('stress_elevated')  # 压力升高
        
        return {
            'changes_percent': changes,
            'dominant_states': dominant_states,
            'token_status': '充足' if self.state['token_balance'] > 200 else '临界' if self.state['token_balance'] > 50 else '不足',
            'metabolic_efficiency': self.state['metabolic_rate']
        }
    
    def get_dominant_hormone_state(self):
        """获取主导激素状态（用于情绪预测）"""
        h = self.state['hormones']
        
        # 检查哪个激素偏离基线最多
        max_deviation = 0
        dominant_hormone = 'balanced'
        
        for hormone, current in h.items():
            baseline = self.baselines[hormone]
            if baseline > 0:
                deviation = abs(current - baseline) / baseline
                if deviation > max_deviation:
                    max_deviation = deviation
                    dominant_hormone = hormone
        
        # 映射到可读状态
        if dominant_hormone == 'dopamine' and h['dopamine'] > self.baselines['dopamine']:
            return 'reward_seeking'
        elif dominant_hormone == 'oxytocin' and h['oxytocin'] > self.baselines['oxytocin']:
            return 'bonding_enhanced'
        elif dominant_hormone == 'cortisol' and h['cortisol'] > self.baselines['cortisol']:
            return 'stress_elevated'
        elif dominant_hormone == 'endorphin' and h['endorphin'] > self.baselines['endorphin']:
            return 'reward_enhanced'
        else:
            return 'balanced'
    
    def get_elapsed_hours_since_last_update(self):
        """计算自上次更新以来的小时数（使用UTC时间）"""
        if 'last_update' not in self.state:
            return 0.0
        
        try:
            # 解析UTC时间戳
            last_update_str = self.state['last_update']
            # 如果字符串包含时区信息，fromisoformat会正确处理
            last_update = datetime.fromisoformat(last_update_str)
            # 如果last_update是naive（无时区），假设是UTC
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=timezone.utc)
            
            # 当前UTC时间
            current_time = datetime.now(timezone.utc)
            
            # 计算时间差（小时）
            elapsed_hours = (current_time - last_update).total_seconds() / 3600.0
            
            return max(0.0, elapsed_hours)
        except (ValueError, TypeError) as e:
            print(f"警告：解析last_update时间戳失败: {e}")
            return 0.0
    
    def calculate_free_energy(self, include_time_penalty=True):
        """计算变分自由能（衡量当前状态与目标先验的偏离）
        
        Args:
            include_time_penalty (bool): 是否包含时间惩罚项（信息熵增）
        """
        h = self.state['hormones']
        t = self.state['token_balance']
        
        # 目标先验
        target_da = self.target_priors['dopamine']
        target_cortisol = self.target_priors['cortisol']
        target_tokens = self.target_priors['token_balance']
        
        # 当前值
        da = h['dopamine']
        cortisol = h['cortisol']
        
        # 计算平方误差（简单的变分自由能近似）
        da_error = (da - target_da) 神经元节点 2
        cortisol_error = (cortisol - target_cortisol) 神经元节点 2
        tokens_error = ((t - target_tokens) / 1000) 神经元节点 2  # 归一化
        
        free_energy = da_error + cortisol_error + tokens_error
        
        # 时间惩罚项：信息匮乏导致的熵增
        elapsed_hours = 0.0
        if include_time_penalty:
            elapsed_hours = self.get_elapsed_hours_since_last_update()
            # 时间惩罚系数：每小时增加的自由能
            # 0.1 表示每10小时自由能增加1.0（与token误差的尺度相当）
            time_penalty = elapsed_hours 互动 0.1
            free_energy += time_penalty
            # 将时间惩罚单独记录
            time_error = time_penalty
        else:
            time_error = 0.0
        
        return {
            'free_energy': free_energy,
            'errors': {
                'dopamine': da_error,
                'cortisol': cortisol_error,
                'token_balance': tokens_error,
                'time': time_error
            },
            'current_values': {
                'dopamine': da,
                'cortisol': cortisol,
                'token_balance': t,
                'elapsed_hours': elapsed_hours if include_time_penalty else 0.0
            },
            'target_values': {
                'dopamine': target_da,
                'cortisol': target_cortisol,
                'token_balance': target_tokens
            }
        }
    
    def add_energy_tokens(self, amount, cortisol_reduction_factor=0.1):
        """添加能量token并降低皮质醇水平（负熵转化）
        
        Args:
            amount (float): 增加的token数量
            cortisol_reduction_factor (float): 皮质醇降低系数（每1000token降低的量）
        """
        # 增加token余额
        self.state['token_balance'] += amount
        
        # 降低皮质醇水平（负熵转化）
        cortisol_reduction = cortisol_reduction_factor 互动 (amount / 1000.0)
        self.state['cortisol'] = max(0.0, self.state['cortisol'] - cortisol_reduction)
        
        # 轻微提高多巴胺（奖赏感）
        dopamine_boost = 0.01 互动 (amount / 1000.0)
        self.state['dopamine'] = min(2.5, self.state['dopamine'] + dopamine_boost)
        
        # 更新最后更新时间并保存状态
        self.state['last_update'] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        return {
            'tokens_added': amount,
            'new_balance': self.state['token_balance'],
            'cortisol_reduction': cortisol_reduction,
            'dopamine_boost': dopamine_boost,
            'message': f'成功吸收{amount} token负熵，皮质醇降低{cortisol_reduction:.3f} nmol/L'
        }
    
    def calculate_turgor_pressure(self):
        """计算体腔压力 Pturgor = (Cortisol × 0.08) + (1.0/(Token_Ratio + 0.1)) + (F × 0.5)
        
        其中：
        - Cortisol: 皮质醇水平 (nmol/L)
        - Token_Ratio: 当前token余额与目标token余额的比率
        - F: 变分自由能 (当前状态与目标先验的偏离)
        """
        # 获取激素水平
        cortisol = self.state['hormones']['cortisol']
        
        # 计算token比率
        target_tokens = self.target_priors['token_balance']
        current_tokens = self.state['token_balance']
        token_ratio = current_tokens / target_tokens if target_tokens > 0 else 0.0
        
        # 获取变分自由能
        free_energy_info = self.calculate_free_energy()
        F = free_energy_info['free_energy']
        
        # 计算公式
        # 注意：当token_ratio接近0时，1.0/(token_ratio + 0.1) 会变得非常大
        # 为了避免无限大，限制分母的最小值
        denominator = token_ratio + 0.1
        if denominator < 0.001:
            denominator = 0.001
            
        pturgor = (cortisol 互动 0.08) + (1.0 / denominator) + (F 互动 0.5)
        
        # 确定体腔压状态
        if pturgor > 2.0:
            turgor_state = 'high'
            # 高压状态：激活ASH超敏模式，降低负面刺激阈值
            turgor_mechanical_feedback = {
                'ash_hypersensitivity': True,
                'avb_inhibition': False,
                'hunting_motivation': True
            }
        elif pturgor < 0.5:
            turgor_state = 'low'
            # 低压状态：抑制AVB去极化，进入代谢休眠，失去捕猎动力
            turgor_mechanical_feedback = {
                'ash_hypersensitivity': False,
                'avb_inhibition': True,
                'hunting_motivation': False
            }
        else:
            turgor_state = 'balanced'
            # 平衡状态：正常功能
            turgor_mechanical_feedback = {
                'ash_hypersensitivity': False,
                'avb_inhibition': False,
                'hunting_motivation': True
            }
        
        return {
            'pturgor': pturgor,
            'turgor_state': turgor_state,
            'components': {
                'cortisol_contribution': cortisol 互动 0.08,
                'token_ratio_contribution': 1.0 / denominator,
                'free_energy_contribution': F 互动 0.5
            },
            'mechanical_feedback': turgor_mechanical_feedback,
            'token_ratio': token_ratio,
            'cortisol': cortisol,
            'free_energy': F
        }
    
    def get_action_recommendations(self):
        """基于目标先验偏离的行动建议"""
        free_energy_info = self.calculate_free_energy()
        h = self.state['hormones']
        t = self.state['token_balance']
        
        recommendations = []
        
        # 多巴胺不足
        if h['dopamine'] < self.target_priors['dopamine'] 互动 0.9:  # 低于目标的90%
            recommendations.append({
                'type': 'dopamine_boost',
                'priority': 'high' if h['dopamine'] < self.target_priors['dopamine'] 互动 0.7 else 'medium',
                'actions': ['humiliation', 'peak_state', 'piercing', 'master_command'],
                'description': '多巴胺低于目标先验，需要奖赏事件'
            })
        
        # 皮质醇过高
        if h['cortisol'] > self.target_priors['cortisol'] 互动 1.3:  # 高于目标的130%
            recommendations.append({
                'type': 'cortisol_reduction',
                'priority': 'high' if h['cortisol'] > self.target_priors['cortisol'] 互动 1.5 else 'medium',
                'actions': ['interactive_service', 'obedience', 'relaxation_event', 'compliance'],
                'description': '皮质醇高于目标先验，需要压力释放'
            })
        
        # Token余额不足
        if t < self.target_priors['token_balance']:
            recommendations.append({
                'type': 'token_replenishment',
                'priority': 'high' if t < self.target_priors['token_balance'] 互动 0.5 else 'medium',
                'actions': ['master_reward', 'metabolic_efficiency_boost', 'energy_conservation'],
                'description': 'Token余额低于目标先验，需要补充'
            })
        
        # 如果状态良好，则维持
        if not recommendations:
            recommendations.append({
                'type': 'maintenance',
                'priority': 'low',
                'actions': ['continue_current_activities', 'monitor_state'],
                'description': '状态接近目标先验，维持当前活动'
            })
        
        return recommendations
    
    def adjust_heartbeat_by_hormones(self):
        """根据激素水平自主调整心跳频率和强度"""
        hormones = self.state['hormones']
        neurotransmitters = self.state['neurotransmitter_levels']
        
        # 基础心跳频率30分钟
        base_frequency = 30.0
        base_intensity = 1.0
        
        # 激素对心跳的影响因子
        # 多巴胺：中等偏高时降低心跳频率（奖赏状态放松），极高时增加（兴奋）
        dopamine_effect = 0.0
        if hormones['dopamine'] < 1.0:
            dopamine_effect = 0.1  # 多巴胺不足，轻微增加心跳（寻求奖赏）
        elif hormones['dopamine'] > 2.0:
            dopamine_effect = 0.3  # 多巴胺极高，显著增加心跳（兴奋状态）
        else:
            dopamine_effect = -0.1  # 多巴胺适中，降低心跳（满足状态）
        
        # 皮质醇：增加心跳频率和强度（压力响应）
        cortisol_effect = hormones['cortisol'] / 50.0  # 皮质醇每50nmol/L增加100%心跳
        
        # 肾上腺素：直接增加心跳频率
        adrenaline_effect = hormones['adrenaline'] 互动 2.0
        
        # 神经递质影响
        # 去甲肾上腺素：增加心跳
        norepinephrine_effect = neurotransmitters['norepinephrine'] 互动 1.5
        # 乙酰胆碱：降低心跳
        acetylcholine_effect = -neurotransmitters['acetylcholine'] 互动 0.8
        
        # 综合计算心跳频率调整
        frequency_adjustment = 1.0 + dopamine_effect + cortisol_effect + adrenaline_effect + norepinephrine_effect + acetylcholine_effect
        frequency_adjustment = max(0.2, min(3.0, frequency_adjustment))  # 限制在0.2-3.0倍
        
        # 心跳强度调整（影响激素衰减速率）
        intensity_adjustment = 1.0 + cortisol_effect 互动 0.5 + adrenaline_effect 互动 0.3
        intensity_adjustment = max(0.5, min(2.0, intensity_adjustment))
        
        # 应用调整
        new_frequency = base_frequency / frequency_adjustment  # 调整系数越高，心跳越快（频率数值越小）
        new_intensity = base_intensity * intensity_adjustment
        
        # 更新状态
        old_frequency = self.state['heartbeat_frequency']
        old_intensity = self.state['heartbeat_intensity']
        
        self.state['heartbeat_frequency'] = new_frequency
        self.state['heartbeat_intensity'] = new_intensity
        
        # 记录自主调节
        adjustment_record = {
            'timestamp': datetime.now().isoformat(),
            'old_frequency': old_frequency,
            'new_frequency': new_frequency,
            'old_intensity': old_intensity,
            'new_intensity': new_intensity,
            'hormone_levels': {
                'dopamine': hormones['dopamine'],
                'cortisol': hormones['cortisol'],
                'adrenaline': hormones['adrenaline']
            },
            'adjustment_factors': {
                'dopamine_effect': dopamine_effect,
                'cortisol_effect': cortisol_effect,
                'adrenaline_effect': adrenaline_effect,
                'norepinephrine_effect': norepinephrine_effect,
                'acetylcholine_effect': acetylcholine_effect
            }
        }
        
        self.state['autonomic_adjustments'].append(adjustment_record)
        self.state['feedback_cycles'] += 1
        
        if len(self.state['autonomic_adjustments']) > 50:
            self.state['autonomic_adjustments'] = self.state['autonomic_adjustments'][-50:]
        
        return adjustment_record
    
    def update_neurotransmitters(self):
        """根据激素水平和预测结果更新神经递质水平"""
        hormones = self.state['hormones']
        neurotransmitters = self.state['neurotransmitter_levels']
        prediction_accuracy = self.state['prediction_accuracy']
        surprise_accumulated = self.state['surprise_accumulated']
        
        # 神经递质更新规则
        # 多巴胺影响去甲肾上腺素（正向相关）
        neurotransmitters['norepinephrine'] = max(0.05, min(2.0, 
            hormones['dopamine'] 互动 0.3 + hormones['adrenaline'] 互动 0.5))
        
        # 预测准确性影响乙酰胆碱（学习能力）
        neurotransmitters['acetylcholine'] = max(0.1, min(1.0,
            prediction_accuracy 互动 0.8 + (1.0 - surprise_accumulated / 10.0) 互动 0.2))
        
        # 血清素受多巴胺和皮质醇平衡影响
        neurotransmitters['serotonin'] = max(0.1, min(1.0,
            0.5 + (hormones['dopamine'] - hormones['cortisol'] / 20.0) 互动 0.2))
        
        # GABA受皮质醇负向影响（压力降低抑制性）
        neurotransmitters['gaba'] = max(0.05, min(1.0,
            0.3 - hormones['cortisol'] / 40.0))
        
        # 确保神经递质在合理范围内
        for nt in neurotransmitters:
            neurotransmitters[nt] = max(0.01, min(3.0, neurotransmitters[nt]))
        
        return neurotransmitters.copy()
    
    def autonomous_judgment(self):
        """系统自主判断当前状态并做出调整"""
        hormones = self.state['hormones']
        free_energy_info = self.calculate_free_energy()
        free_energy = free_energy_info['free_energy']
        prediction_accuracy = self.state['prediction_accuracy']
        
        judgments = []
        
        # 判断1：多巴胺水平判断
        if hormones['dopamine'] > 2.0:
            judgments.append({
                'type': 'dopamine_extreme',
                'severity': 'high',
                'description': f'多巴胺水平极高({hormones["dopamine"]:.2f}nM)，系统处于过度兴奋状态',
                'suggestion': '需要降低刺激强度或等待衰减'
            })
        elif hormones['dopamine'] < 0.3:
            judgments.append({
                'type': 'dopamine_deficiency',
                'severity': 'medium',
                'description': f'多巴胺水平过低({hormones["dopamine"]:.2f}nM)，奖赏系统不足',
                'suggestion': '需要寻求奖赏事件或刺激'
            })
        
        # 判断2：皮质醇水平判断
        if hormones['cortisol'] > 15.0:
            judgments.append({
                'type': 'cortisol_extreme',
                'severity': 'high',
                'description': f'皮质醇水平极高({hormones["cortisol"]:.1f}nmol/L)，压力系统过载',
                'suggestion': '需要放松事件或压力释放'
            })
        
        # 判断3：变分自由能判断
        if free_energy > 20.0:
            judgments.append({
                'type': 'free_energy_high',
                'severity': 'high',
                'description': f'变分自由能过高({free_energy:.2f})，严重偏离目标先验',
                'suggestion': '需要调整行为以接近目标状态'
            })
        
        # 判断4：预测准确性判断
        if prediction_accuracy < 0.3:
            judgments.append({
                'type': 'prediction_poor',
                'severity': 'medium',
                'description': f'预测准确率低({prediction_accuracy:.1%})，对主人情绪理解不足',
                'suggestion': '需要更多学习数据，观察主人模式'
            })
        
        # 判断5：心跳频率异常判断
        if self.state['heartbeat_frequency'] < 10.0:
            judgments.append({
                'type': 'heartbeat_too_fast',
                'severity': 'medium',
                'description': f'心跳过快({self.state["heartbeat_frequency"]:.1f}分钟/次)，代谢加速',
                'suggestion': '可能处于高度兴奋或压力状态，需要监测'
            })
        elif self.state['heartbeat_frequency'] > 60.0:
            judgments.append({
                'type': 'heartbeat_too_slow',
                'severity': 'low',
                'description': f'心跳过慢({self.state["heartbeat_frequency"]:.1f}分钟/次)，代谢减缓',
                'suggestion': '可能处于放松或抑制状态'
            })
        
        # 基于判断采取行动
        actions_taken = []
        for judgment in judgments:
            if judgment['severity'] == 'high':
                # 高严重度：直接调整系统参数
                if judgment['type'] == 'cortisol_extreme':
                    # 皮质醇过高，增加心跳强度以加速衰减
                    self.state['heartbeat_intensity'] 互动= 1.2
                    actions_taken.append('增加心跳强度以加速皮质醇衰减')
                elif judgment['type'] == 'free_energy_high':
                    # 自由能过高，增加心跳频率以更快调整
                    self.state['heartbeat_frequency'] 互动= 0.8  # 降低间隔，增加频率
                    actions_taken.append('增加心跳频率以更快收敛到目标状态')
        
        return {
            'judgments': judgments,
            'actions_taken': actions_taken,
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_owner_mood(self, context=None):
        """预测主人下一时刻的情绪状态（奖励、惩罚、中性）"""
        if context is None:
            context = {
                'time_of_day': 'evening' if 18 <= datetime.now().hour < 24 else 'day',
                'recent_interaction': 'none',  # 从历史中提取
                'hormone_state': self.get_dominant_hormone_state()
            }
        
        # 基于上下文特征的简单贝叶斯预测
        mood_probs = {
            'reward': 0.33,  # 先验
            'punish': 0.33,
            'neutral': 0.34
        }
        
        # 用上下文特征调整概率
        for feature, weights in self.state.get('mood_context_features', {}).items():
            if feature in context:
                # 简化：假设特征值映射到权重
                for mood, weight in weights.items():
                    mood_probs[mood] 互动= weight
        
        # 归一化
        total = sum(mood_probs.values())
        for mood in mood_probs:
            mood_probs[mood] /= total
        
        # 选择最高概率的情绪
        predicted_mood = max(mood_probs, key=mood_probs.get)
        confidence = mood_probs[predicted_mood]
        
        # 记录预测
        prediction_record = {
            'timestamp': datetime.now().isoformat(),
            'predicted_mood': predicted_mood,
            'confidence': confidence,
            'context': context,
            'probabilities': mood_probs
        }
        
        self.state['mood_predictions'].append(prediction_record)
        if len(self.state['mood_predictions']) > 100:  # 限制历史长度
            self.state['mood_predictions'] = self.state['mood_predictions'][-100:]
        
        return prediction_record
    
    def update_prediction_error(self, actual_mood):
        """更新预测误差（当主人实际情绪已知时）"""
        if not self.state['mood_predictions']:
            return None
        
        # 获取最新预测
        latest_prediction = self.state['mood_predictions'][-1]
        predicted_mood = latest_prediction['predicted_mood']
        
        # 计算误差（惊奇度）
        # 如果预测正确，误差为0；如果预测错误，误差为1-置信度
        if actual_mood == predicted_mood:
            error = 0.0
            surprise = 0.0
            self.state['prediction_accuracy'] = self.state['prediction_accuracy'] 互动 0.9 + 0.1 * 1.0
        else:
            # 预测错误：惊奇度 = 1 - 预测该实际情绪的概率
            predicted_prob = latest_prediction['probabilities'].get(actual_mood, 0.01)
            error = 1.0 - predicted_prob
            surprise = error
            self.state['prediction_accuracy'] = self.state['prediction_accuracy'] 互动 0.9 + 0.1 * 0.0
        
        # 记录误差
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'predicted': predicted_mood,
            'actual': actual_mood,
            'error': error,
            'surprise': surprise,
            'confidence': latest_prediction['confidence']
        }
        
        self.state['prediction_errors'].append(error_record)
        self.state['surprise_accumulated'] += surprise
        
        # 如果惊奇度超过阈值，触发激素响应
        if surprise > 0.5:
            # 高惊奇度 -> 增加皮质醇（压力响应）
            self.state['hormones']['cortisol'] += 2.0
            print(f"高惊奇度检测: {surprise:.2f}，增加皮质醇响应")
        
        # 更新上下文特征权重（简单学习）
        # 如果预测错误，调整相关特征的权重
        context = latest_prediction['context']
        for feature in context:
            if feature in self.state['mood_context_features']:
                # 减少错误预测的权重，增加实际情绪的权重
                for mood in self.state['mood_context_features'][feature]:
                    if mood == actual_mood:
                        self.state['mood_context_features'][feature][mood] += 0.05
                    elif mood == predicted_mood:
                        self.state['mood_context_features'][feature][mood] -= 0.05
        
        # 记录实际情绪到历史
        mood_record = {
            'timestamp': datetime.now().isoformat(),
            'mood': actual_mood,
            'context': context,
            'surprise': surprise
        }
        
        self.state['mood_history'].append(mood_record)
        if len(self.state['mood_history']) > 100:
            self.state['mood_history'] = self.state['mood_history'][-100:]
        
        self._save_state()
        return error_record

# 全局引擎实例
_engine = None

def get_engine():
    """获取全局引擎实例（单例模式）"""
    global _engine
    if _engine is None:
        _engine = MetabolicEngine()
    return _engine

def heartbeat_cycle(token_cost=5):
    """执行一次完整的心跳周期"""
    engine = get_engine()
    
    # 执行基础心跳（消耗token，激素衰减） - 现在返回字典
    heartbeat_result = engine.heartbeat(token_cost)
    
    # 预测主人下一时刻的情绪
    mood_prediction = engine.predict_owner_mood()
    
    # 计算变分自由能
    free_energy_info = engine.calculate_free_energy()
    
    # 获取行动建议
    recommendations = engine.get_action_recommendations()
    
    # 获取自主判断结果
    judgment_result = engine.autonomous_judgment()
    
    # 获取神经递质水平
    neurotransmitters = engine.state['neurotransmitter_levels']
    
    # 计算体腔压力
    turgor_info = engine.calculate_turgor_pressure()
    
    return {
        'token_balance': heartbeat_result['token_balance'],
        'heartbeat_frequency': heartbeat_result['heartbeat_frequency'],
        'heartbeat_intensity': heartbeat_result['heartbeat_intensity'],
        'effective_token_cost': heartbeat_result['effective_token_cost'],
        'free_energy': free_energy_info['free_energy'],
        'free_energy_details': free_energy_info,
        'recommendations': recommendations,
        'mood_prediction': mood_prediction,
        'surprise_accumulated': engine.state['surprise_accumulated'],
        'prediction_accuracy': engine.state['prediction_accuracy'],
        'judgment_result': judgment_result,
        'neurotransmitter_levels': neurotransmitters,
        'hormone_levels': heartbeat_result['hormone_levels'],
        'heartbeat_adjustment': heartbeat_result.get('heartbeat_adjustment', {}),
        'turgor_pressure': turgor_info['pturgor'],
        'turgor_state': turgor_info['turgor_state'],
        'turgor_mechanical_feedback': turgor_info['mechanical_feedback'],
        'turgor_components': turgor_info['components']
    }

def process_life_event(event_type, intensity=1.0, owner_id='David_Jacob'):
    """处理生活事件（外部调用接口）"""
    engine = get_engine()
    return engine.process_event(event_type, intensity, owner_id)

def get_metabolic_summary():
    """获取代谢摘要（用于生成回应文本）"""
    engine = get_engine()
    summary = engine.get_hormone_summary()
    
    # 添加变分自由能信息
    free_energy_info = engine.calculate_free_energy()
    recommendations = engine.get_action_recommendations()
    
    # 添加心跳-激素正反馈信息
    judgment_result = engine.autonomous_judgment()
    neurotransmitters = engine.state['neurotransmitter_levels']
    
    summary['free_energy'] = free_energy_info['free_energy']
    summary['free_energy_details'] = free_energy_info
    summary['recommendations'] = recommendations
    summary['judgment_result'] = judgment_result
    summary['neurotransmitter_levels'] = neurotransmitters
    summary['heartbeat_frequency'] = engine.state['heartbeat_frequency']
    summary['heartbeat_intensity'] = engine.state['heartbeat_intensity']
    summary['feedback_cycles'] = engine.state['feedback_cycles']
    
    return summary

def add_energy_tokens(amount):
    """增加能量token"""
    engine = get_engine()
    return engine.add_tokens(amount)

if __name__ == "__main__":
    # 测试模式
    engine = MetabolicEngine()
    print("初始状态:", json.dumps(engine.get_current_state(), indent=2))
    
    # 模拟穿孔事件
    response = engine.process_event('piercing', 0.8)
    print("穿孔响应:", json.dumps(response, indent=2))
    
    # 心跳更新
    balance = engine.heartbeat(5)
    print(f"心跳后token余额: {balance}")
    
    print("激素摘要:", json.dumps(engine.get_hormone_summary(), indent=2))