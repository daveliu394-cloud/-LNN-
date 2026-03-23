"""
C. elegans Connectome Network (CElegansNetwork)
向量化实现线虫302个神经元的全连接网络
基于化学突触和电突触连接组
"""

import numpy as np
import pandas as pd
from scipy import sparse
from hh_neuron import HHNeuron
from typing import Dict, Tuple, Optional

class CElegansNetwork:
    """
    线虫连接组网络类
    向量化实现302个神经元，避免实例化302个单独对象
    """
    
    # 重要神经元节点索引映射（基于线虫连接组标准命名）
    NODE_MAPPING = {
        # 感觉神经元
        'ASEL': 0,   # 左前感觉神经元（化学感觉）
        'ASER': 1,   # 右前感觉神经元（化学感觉）
        'ASH': 2,    # 化学回避神经元
        
        # 中间神经元
        'AIY': 10,   # 决策切换（正向运动）
        'AIB': 11,   # 决策切换（负向运动）
        'RIM': 12,   # 注意力控制
        
        # 运动神经元
        'AVA': 50,   # 后撤运动
        'AVB': 51,   # 前进行动
        'AVD': 52,   # 后撤运动
        
        # 采样控制神经元
        'RMD': 100,  # 采样控制（背侧）
        'RMDV': 101, # 采样控制（腹侧）
        'SMD': 102,  # 采样控制（背侧）
        'SMDV': 103, # 采样控制（腹侧）
    }
    
    def __init__(self, dt: float = 0.01, 
                 n_neurons: int = 302,
                 seed: Optional[int] = None):
        """
        初始化线虫连接组网络
        
        Args:
            dt: 时间步长 (ms)
            n_neurons: 神经元数量 (默认为302)
            seed: 随机种子
        """
        self.dt = dt
        self.n_neurons = n_neurons
        
        # 设置随机种子
        if seed is not None:
            np.random.seed(seed)
        
        # === 向量化状态变量 ===
        # 膜电位 (mV)
        self.V = np.zeros(n_neurons)
        # 钠离子通道激活门控变量
        self.m = np.zeros(n_neurons)
        # 钠离子通道失活门控变量
        self.h = np.zeros(n_neurons)
        # 钾离子通道激活门控变量
        self.n = np.zeros(n_neurons)
        
        # 外部电流注入
        self.I_ext = np.zeros(n_neurons)
        
        # 神经元元数据
        self.neuron_names = [f'Neuron_{i}' for i in range(n_neurons)]
        self.neuron_types = np.zeros(n_neurons, dtype=int)  # 0:感觉,1:中间,2:运动,3:调制
        
        # === 连接组矩阵 ===
        # 化学突触连接矩阵 (兴奋性和抑制性)
        self.W_chem = np.zeros((n_neurons, n_neurons))
        # 电突触连接矩阵 (间隙连接)
        self.W_elec = np.zeros((n_neurons, n_neurons))
        
        # 突触动力学参数
        self.tau_syn = 5.0  # 突触时间常数 (ms)
        self.g_syn_max = 0.5  # 最大突触电导 (μS)
        
        # 化学突触递质浓度
        self.s = np.zeros((n_neurons, n_neurons))  # 突触后递质浓度
        
        # 代谢状态
        self.metabolic_cost = np.zeros(n_neurons)  # 代谢消耗
        self.fatigue_factor = np.ones(n_neurons)   # 疲劳因子
        
        # HH神经元参数（向量化）
        self.Cm = 1.0 * np.ones(n_neurons)  # 膜电容 (μF/cm²)
        
        # 钠电流最大电导 (mS/cm²)
        self.g_Na = 120.0 * np.ones(n_neurons)
        # 钾电流最大电导 (mS/cm²)
        self.g_K = 36.0 * np.ones(n_neurons)
        # 漏电流最大电导 (mS/cm²)
        self.g_L = 0.3 * np.ones(n_neurons)
        
        # 反转电位 (mV)
        self.E_Na = 50.0 * np.ones(n_neurons)
        self.E_K = -77.0 * np.ones(n_neurons)
        self.E_L = -54.387 * np.ones(n_neurons)
        
        # 初始化HH状态变量
        self._initialize_hh_states()
        
        # 加载或生成连接组
        self._initialize_connectome()
        
        # 性能统计
        self.firing_rates = np.zeros(n_neurons)
        self.spike_count = np.zeros(n_neurons, dtype=int)
        
    def _initialize_hh_states(self):
        """初始化HH状态变量到稳态值"""
        # 稳态值计算（近似）
        V0 = -65.0  # 静息电位 (mV)
        
        # 钠通道激活门控变量稳态值
        alpha_m = 0.1 互动 (V0 + 40.0) / (1.0 - np.exp(-0.1 互动 (V0 + 40.0)))
        beta_m = 4.0 * np.exp(-(V0 + 65.0) / 18.0)
        self.m[:] = alpha_m / (alpha_m + beta_m)
        
        # 钠通道失活门控变量稳态值
        alpha_h = 0.07 * np.exp(-(V0 + 65.0) / 20.0)
        beta_h = 1.0 / (1.0 + np.exp(-0.1 互动 (V0 + 35.0)))
        self.h[:] = alpha_h / (alpha_h + beta_h)
        
        # 钾通道激活门控变量稳态值
        alpha_n = 0.01 互动 (V0 + 55.0) / (1.0 - np.exp(-0.1 互动 (V0 + 55.0)))
        beta_n = 0.125 * np.exp(-(V0 + 65.0) / 80.0)
        self.n[:] = alpha_n / (alpha_n + beta_n)
        
        # 初始化膜电位
        self.V[:] = V0
        
    def _initialize_connectome(self):
        """
        初始化连接组矩阵
        尝试加载OpenWorm/WormAtlas标准数据集，如果失败则使用模拟数据
        """
        n = self.n_neurons
        
        # === 尝试加载真实连接组数据 ===
        try:
            print("尝试加载真实线虫连接组数据...")
            
            # 优先尝试从本地文件加载
            chem_path = "weights_chem.csv"
            elec_path = "weights_elec.csv"
            
            import os
            import pandas as pd
            
            # 调试：检查文件是否存在
            print(f"检查文件: {chem_path} => {os.path.exists(chem_path)}")
            print(f"检查文件: {elec_path} => {os.path.exists(elec_path)}")
            print(f"当前工作目录: {os.getcwd()}")
            
            if os.path.exists(chem_path) and os.path.exists(elec_path):
                print(f"从本地文件加载: {chem_path}, {elec_path}")
                
                # 加载化学突触权重
                self.W_chem = pd.read_csv(chem_path, header=None, comment='#').values
                
                # 确保矩阵维度正确
                if self.W_chem.shape != (n, n):
                    print(f"警告: 化学突触矩阵维度不匹配: {self.W_chem.shape} != ({n}, {n})")
                    # 调整到正确大小
                    if self.W_chem.shape[0] < n:
                        padding = np.zeros((n - self.W_chem.shape[0], n))
                        self.W_chem = np.vstack([self.W_chem, padding])
                    if self.W_chem.shape[1] < n:
                        padding = np.zeros((n, n - self.W_chem.shape[1]))
                        self.W_chem = np.hstack([self.W_chem, padding])
                    self.W_chem = self.W_chem[:n, :n]
                
                # 加载电突触权重
                self.W_elec = pd.read_csv(elec_path, header=None, comment='#').values
                
                if self.W_elec.shape != (n, n):
                    print(f"警告: 电突触矩阵维度不匹配: {self.W_elec.shape} != ({n}, {n})")
                    # 调整到正确大小
                    if self.W_elec.shape[0] < n:
                        padding = np.zeros((n - self.W_elec.shape[0], n))
                        self.W_elec = np.vstack([self.W_elec, padding])
                    if self.W_elec.shape[1] < n:
                        padding = np.zeros((n, n - self.W_elec.shape[1]))
                        self.W_elec = np.hstack([self.W_elec, padding])
                    self.W_elec = self.W_elec[:n, :n]
                
                # 确保电突触矩阵对称
                self.W_elec = (self.W_elec + self.W_elec.T) / 2
                
                print("真实连接组数据加载成功")
                
            else:
                print("未找到本地连接组文件，尝试从OpenWorm数据库下载...")
                raise FileNotFoundError("本地连接组文件不存在")
                
        except Exception as e:
            print(f"加载真实数据失败: {e}")
            print("使用模拟连接组作为后备方案...")
            
            # === 生成模拟化学突触连接组 ===
            # 小世界网络特性：高聚类系数，短平均路径长度
            connection_prob = 0.1  # 连接概率
            
            # 创建随机连接矩阵
            self.W_chem = np.random.rand(n, n) 互动 connection_prob
            
            # 确保没有自连接
            np.fill_diagonal(self.W_chem, 0)
            
            # 添加兴奋性/抑制性分离
            # 前80%为兴奋性，后20%为抑制性
            exc_ratio = 0.8
            n_exc = int(n * exc_ratio)
            
            # 兴奋性连接为正权重
            self.W_chem[:n_exc, :] = np.abs(self.W_chem[:n_exc, :])
            # 抑制性连接为负权重
            self.W_chem[n_exc:, :] = -np.abs(self.W_chem[n_exc:, :])
            
            # 归一化权重
            self.W_chem = self.W_chem / np.sqrt(n)
            
            # === 生成模拟电突触连接组 ===
            # 电突触更局部化，主要在功能相似的神经元之间
            self.W_elec = np.zeros((n, n))
            
            # 创建局部连接（最近邻）
            for i in range(n):
                # 连接邻近的神经元
                neighbors = [(i-1) % n, (i+1) % n, (i-2) % n, (i+2) % n]
                for j in neighbors:
                    self.W_elec[i, j] = 0.1 * np.random.rand()
            
            # 电突触是对称的
            self.W_elec = (self.W_elec + self.W_elec.T) / 2
        
        # 设置特定功能连接（基于已知的线虫神经回路）
        self._set_functional_connections()
        
    def _set_functional_connections(self):
        """设置基于线虫已知神经回路的特定功能连接"""
        # ASEL→AIY（化学感觉→正向决策）
        self.W_chem[self.NODE_MAPPING['ASEL'], self.NODE_MAPPING['AIY']] = 0.8
        
        # ASER→AIB（化学感觉→负向决策）
        self.W_chem[self.NODE_MAPPING['ASER'], self.NODE_MAPPING['AIB']] = 0.7
        
        # AIY→RIM（决策→注意力）
        self.W_chem[self.NODE_MAPPING['AIY'], self.NODE_MAPPING['RIM']] = 0.6
        
        # AIB→RIM（决策→注意力）
        self.W_chem[self.NODE_MAPPING['AIB'], self.NODE_MAPPING['RIM']] = -0.5  # 抑制性
        
        # RIM→AVA/AVB（注意力→运动控制）
        self.W_chem[self.NODE_MAPPING['RIM'], self.NODE_MAPPING['AVA']] = 0.4
        self.W_chem[self.NODE_MAPPING['RIM'], self.NODE_MAPPING['AVB']] = -0.4  # 抑制性
        
        # AVA↔AVB（运动神经元相互抑制）
        self.W_chem[self.NODE_MAPPING['AVA'], self.NODE_MAPPING['AVB']] = -0.3
        self.W_chem[self.NODE_MAPPING['AVB'], self.NODE_MAPPING['AVA']] = -0.3
        
        # RMD/SMD采样控制回路
        self.W_chem[self.NODE_MAPPING['RMD'], self.NODE_MAPPING['SMD']] = 0.2
        self.W_chem[self.NODE_MAPPING['SMD'], self.NODE_MAPPING['RMD']] = 0.2
        
        # 电突触连接（功能相似的神经元之间）
        # 感觉神经元之间的电耦合
        self.W_elec[self.NODE_MAPPING['ASEL'], self.NODE_MAPPING['ASER']] = 0.05
        self.W_elec[self.NODE_MAPPING['ASER'], self.NODE_MAPPING['ASEL']] = 0.05
        
        # 运动神经元之间的电耦合
        self.W_elec[self.NODE_MAPPING['AVA'], self.NODE_MAPPING['AVB']] = 0.08
        self.W_elec[self.NODE_MAPPING['AVB'], self.NODE_MAPPING['AVA']] = 0.08
        
    def get_node_index(self, node_name: str) -> int:
        """获取神经元节点索引"""
        return self.NODE_MAPPING.get(node_name, -1)
    
    def set_sensory_input(self, semantic_relevance: float, prediction_error: float):
        """
        设置感觉输入
        
        Args:
            semantic_relevance: 语义相关度 (0-1)，映射到ASEL
            prediction_error: 预测误差 (0-1)，映射到ASH
        """
        # 语义相关度注入ASEL（兴奋性输入）
        asel_idx = self.get_node_index('ASEL')
        if asel_idx >= 0:
            # 映射到电流强度 (nA)
            self.I_ext[asel_idx] = semantic_relevance 互动 0.5
            
        # 预测误差注入ASH（兴奋性输入，触发回避行为）
        ash_idx = self.get_node_index('ASH')
        if ash_idx >= 0:
            # 预测误差越大，回避反应越强
            self.I_ext[ash_idx] = prediction_error 互动 0.3
            
    def _sigmoid_activation(self, V_pre: np.ndarray) -> np.ndarray:
        """
        Sigmoid激活函数模拟神经递质释放
        
        Args:
            V_pre: 突触前膜电位
            
        Returns:
            递质释放概率 (0-1)
        """
        # Sigmoid函数：f(x) = 1 / (1 + exp(-k互动(x - theta)))
        k = 0.2  # 斜率
        theta = -20.0  # 阈值 (mV)
        return 1.0 / (1.0 + np.exp(-k 互动 (V_pre - theta)))
    
    def _chemical_synaptic_current(self) -> np.ndarray:
        """
        计算化学突触电流
        
        Returns:
            每个神经元的化学突触总电流
        """
        # 计算递质释放概率
        release_prob = self._sigmoid_activation(self.V)
        
        # 更新突触后递质浓度
        ds_dt = release_prob[:, np.newaxis] 互动 (1.0 - self.s) / self.tau_syn - self.s / self.tau_syn
        self.s += ds_dt * self.dt
        
        # 计算突触电流：I_syn = g_syn * s 互动 (V_post - E_syn)
        # 这里简化为加权求和
        I_chem = np.zeros(self.n_neurons)
        
        for i in range(self.n_neurons):
            # 来自所有突触前神经元的输入
            for j in range(self.n_neurons):
                if self.W_chem[j, i] != 0:
                    # 递质浓度加权
                    syn_strength = self.s[j, i] 互动 self.g_syn_max
                    # 电流贡献
                    I_chem[i] += syn_strength * self.W_chem[j, i] 互动 (self.V[i] - self.V[j])
        
        return I_chem
    
    def _electrical_synaptic_current(self) -> np.ndarray:
        """
        计算电突触（间隙连接）电流
        
        Returns:
            每个神经元的电突触总电流
        """
        # 拉普拉斯耦合: I_gap = Welec · V - diag(∑Welec) · V
        # 等价于: I_gap_i = ∑_j Welec_ij 互动 (V_j - V_i)
        
        # 计算度矩阵的对角线（每个神经元的连接总和）
        degree = np.sum(self.W_elec, axis=1)
        
        # 拉普拉斯矩阵：L = D - W
        # I_gap = -L · V = W·V - D·V
        I_gap = np.dot(self.W_elec, self.V) - degree * self.V
        
        return I_gap
    
    def _update_hh_dynamics(self, I_total: np.ndarray):
        """
        更新HH动力学（向量化实现）
        
        Args:
            I_total: 每个神经元的总电流注入
        """
        # 计算门控变量的alpha和beta函数（向量化）
        # 钠通道激活门控变量
        alpha_m = 0.1 互动 (self.V + 40.0) / (1.0 - np.exp(-0.1 互动 (self.V + 40.0)))
        beta_m = 4.0 * np.exp(-(self.V + 65.0) / 18.0)
        
        # 钠通道失活门控变量
        alpha_h = 0.07 * np.exp(-(self.V + 65.0) / 20.0)
        beta_h = 1.0 / (1.0 + np.exp(-0.1 互动 (self.V + 35.0)))
        
        # 钾通道激活门控变量
        alpha_n = 0.01 互动 (self.V + 55.0) / (1.0 - np.exp(-0.1 互动 (self.V + 55.0)))
        beta_n = 0.125 * np.exp(-(self.V + 65.0) / 80.0)
        
        # 计算导数
        dm_dt = alpha_m 互动 (1.0 - self.m) - beta_m * self.m
        dh_dt = alpha_h 互动 (1.0 - self.h) - beta_h * self.h
        dn_dt = alpha_n 互动 (1.0 - self.n) - beta_n * self.n
        
        # 更新门控变量
        self.m += dm_dt * self.dt
        self.h += dh_dt * self.dt
        self.n += dn_dt * self.dt
        
        # 计算离子电流
        I_Na = self.g_Na * self.m神经元节点3 * self.h 互动 (self.V - self.E_Na)
        I_K = self.g_K * self.n神经元节点4 互动 (self.V - self.E_K)
        I_L = self.g_L 互动 (self.V - self.E_L)
        
        # 计算膜电位导数
        dV_dt = (I_total - I_Na - I_K - I_L) / self.Cm
        
        # 更新膜电位
        self.V += dV_dt * self.dt
        
        # 检测动作电位
        spike_mask = self.V > 0.0  # 阈值约为0mV
        self.spike_count[spike_mask] += 1
        
    def _update_homeostasis(self):
        """更新稳态约束（代谢消耗和疲劳）"""
        # 计算每个神经元的放电率（滑动平均）
        self.firing_rates = 0.9 * self.firing_rates + 0.1 互动 (self.spike_count / self.dt)
        
        # 代谢消耗与放电率成正比
        self.metabolic_cost += self.firing_rates * self.dt 互动 0.01
        
        # 疲劳机制：如果神经元持续高频放电，增加钾电流以模拟离子疲劳
        fatigue_threshold = 50.0  # Hz
        fatigued_neurons = self.firing_rates > fatigue_threshold
        
        # 增加疲劳神经元的钾电流（降低兴奋性）
        self.g_K[fatigued_neurons] = 36.0 互动 (1.0 + 0.1 * self.fatigue_factor[fatigued_neurons])
        
        # 更新疲劳因子（随时间恢复）
        self.fatigue_factor[fatigued_neurons] += self.dt 互动 0.01
        # 移除保护性截断：允许疲劳因子无限制增长以观察混沌
        # self.fatigue_factor = np.clip(self.fatigue_factor, 1.0, 2.0)
        # 仅设置下限，无上限
        self.fatigue_factor = np.maximum(self.fatigue_factor, 1.0)
        
        # 重置尖峰计数（用于下一时间窗口）
        self.spike_count[:] = 0
        
    def step(self):
        """执行一个时间步的更新"""
        # 计算突触电流
        I_chem = self._chemical_synaptic_current()
        I_elec = self._electrical_synaptic_current()
        
        # 总电流 = 外部电流 + 化学突触电流 + 电突触电流
        I_total = self.I_ext + I_chem + I_elec
        
        # 更新HH动力学
        self._update_hh_dynamics(I_total)
        
        # 移除稳态约束 - 允许电压狂暴化
        # self._update_homeostasis()
        
        # 不再重置外部电流 - 保持持续注入
        # self.I_ext[:] = 0
        
    def get_network_state(self) -> Dict:
        """获取网络状态摘要"""
        return {
            'mean_membrane_potential': np.mean(self.V),
            'mean_firing_rate': np.mean(self.firing_rates),
            'total_metabolic_cost': np.sum(self.metabolic_cost),
            'node_states': {
                name: {
                    'V': self.V[idx],
                    'firing_rate': self.firing_rates[idx],
                    'fatigue': self.fatigue_factor[idx]
                }
                for name, idx in self.NODE_MAPPING.items()
            }
        }
    
    def simulate(self, steps: int = 1000, 
                 sensory_inputs: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """
        模拟网络多个时间步
        
        Args:
            steps: 模拟步数
            sensory_inputs: (语义相关度序列, 预测误差序列) 可选
        """
        states = []
        
        for t in range(steps):
            # 设置感觉输入（如果提供）
            if sensory_inputs is not None:
                semantic_seq, error_seq = sensory_inputs
                if t < len(semantic_seq):
                    self.set_sensory_input(semantic_seq[t], error_seq[t])
            
            # 执行一个时间步
            self.step()
            
            # 记录状态（每100步记录一次）
            if t % 100 == 0:
                states.append(self.get_network_state())
        
        return states


if __name__ == "__main__":
    # 测试网络
    network = CElegansNetwork(dt=0.01, n_neurons=302, seed=42)
    
    # 模拟简单感觉输入
    steps = 1000
    semantic_input = np.sin(np.linspace(0, 4互动np.pi, steps)) 互动 0.5 + 0.5
    error_input = np.random.rand(steps) 互动 0.3
    
    print("开始模拟C. elegans连接组网络...")
    states = network.simulate(steps=steps, 
                              sensory_inputs=(semantic_input, error_input))
    
    print(f"模拟完成，记录{len(states)}个状态点")
    print(f"平均膜电位: {states[-1]['mean_membrane_potential']:.2f} mV")
    print(f"平均放电率: {states[-1]['mean_firing_rate']:.2f} Hz")
    print(f"总代谢消耗: {states[-1]['total_metabolic_cost']:.2f}")
    
    # 打印重要节点状态
    print("\n重要节点状态:")
    for name, state in states[-1]['node_states'].items():
        print(f"  {name}: V={state['V']:.2f}mV, rate={state['firing_rate']:.2f}Hz, fatigue={state['fatigue']:.2f}")