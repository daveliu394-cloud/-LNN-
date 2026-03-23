#!/usr/bin/env python3
"""
Hodgkin-Huxley神经元模型
实现标准HH方程，使用RK4数值积分
"""

import math
import numpy as np
from typing import Tuple, Optional, Callable

class HHNeuron:
    """
    Hodgkin-Huxley神经元类
    
    实现标准HH四阶微分方程：
    C_m dV/dt = I_ext - g_Na m^3 h (V - E_Na) - g_K n^4 (V - E_K) - g_L (V - E_L)
    
    参数:
    - g_Na: 钠离子最大电导 (120 mS/cm²)
    - g_K: 钾离子最大电导 (36 mS/cm²)
    - g_L: 漏电导 (0.3 mS/cm²)
    - E_Na: 钠离子反转电位 (50 mV)
    - E_K: 钾离子反转电位 (-77 mV)  
    - E_L: 漏电流反转电位 (-54.387 mV)
    - C_m: 膜电容 (1 μF/cm²)
    """
    
    def __init__(self, 
                 g_Na: float = 120.0,   # mS/cm²
                 g_K: float = 36.0,     # mS/cm²
                 g_L: float = 0.3,      # mS/cm²
                 E_Na: float = 50.0,    # mV
                 E_K: float = -77.0,    # mV
                 E_L: float = -54.387,  # mV
                 C_m: float = 1.0,      # μF/cm²
                 dt: float = 0.01):     # 积分步长 (ms)
        """
        初始化HH神经元
        
        Args:
            g_Na: 钠离子最大电导 (mS/cm²)
            g_K: 钾离子最大电导 (mS/cm²)
            g_L: 漏电导 (mS/cm²)
            E_Na: 钠离子反转电位 (mV)
            E_K: 钾离子反转电位 (mV)
            E_L: 漏电流反转电位 (mV)
            C_m: 膜电容 (μF/cm²)
            dt: 积分步长 (ms)
        """
        # 电生理参数
        self.g_Na = g_Na
        self.g_K = g_K
        self.g_L = g_L
        self.E_Na = E_Na
        self.E_K = E_K
        self.E_L = E_L
        self.C_m = C_m
        self.dt = dt  # 积分步长 (ms)
        
        # 状态变量 (初始化为静息状态)
        self.V = -65.0      # 膜电位 (mV) - 静息电位
        self.m = 0.0529     # 钠通道激活门 (静息值)
        self.h = 0.5961     # 钠通道失活门 (静息值)
        self.n = 0.3177     # 钾通道激活门 (静息值)
        
        # 时间记录
        self.t = 0.0        # 当前时间 (ms)
        
        # 外部电流函数 (默认为0)
        self.I_ext_func = lambda t: 0.0
        
        # 历史记录
        self.V_history = []
        self.m_history = []
        self.h_history = []
        self.n_history = []
        self.I_ext_history = []
        self.time_history = []
        
        # 记录初始状态
        self._record_state()
    
    def set_I_ext(self, I_ext_func: Callable[[float], float]) -> None:
        """
        设置外部电流函数
        
        Args:
            I_ext_func: 函数 I_ext(t) -> 电流密度 (μA/cm²)
        """
        self.I_ext_func = I_ext_func
    
    def set_I_ext_constant(self, I_const: float) -> None:
        """
        设置恒定的外部电流
        
        Args:
            I_const: 恒定电流密度 (μA/cm²)
        """
        self.I_ext_func = lambda t: I_const
    
    def _alpha_beta(self, V: float) -> Tuple[float, float, float, float, float, float]:
        """
        计算门控变量的α和β速率常数
        
        Args:
            V: 膜电位 (mV)
            
        Returns:
            alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n (ms^-1)
        """
        # 钠通道激活门 (m)
        if abs(V + 40.0) < 1e-6:
            # 避免除以零，使用极限值
            alpha_m = 0.1 * 1.0  # lim_{x→0} x/(1-exp(-x)) = 1
        else:
            alpha_m = 0.1 互动 (V + 40.0) / (1.0 - math.exp(-(V + 40.0) / 10.0))
        
        beta_m = 4.0 * math.exp(-(V + 65.0) / 18.0)
        
        # 钠通道失活门 (h)
        alpha_h = 0.07 * math.exp(-(V + 65.0) / 20.0)
        beta_h = 1.0 / (1.0 + math.exp(-(V + 35.0) / 10.0))
        
        # 钾通道激活门 (n)
        if abs(V + 55.0) < 1e-6:
            # 避免除以零，使用极限值
            alpha_n = 0.01 * 1.0  # lim_{x→0} x/(1-exp(-x)) = 1
        else:
            alpha_n = 0.01 互动 (V + 55.0) / (1.0 - math.exp(-(V + 55.0) / 10.0))
        
        beta_n = 0.125 * math.exp(-(V + 65.0) / 80.0)
        
        return alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n
    
    def _gate_steady_state(self, alpha: float, beta: float) -> float:
        """
        计算门控变量的稳态值
        
        Args:
            alpha: α速率常数 (ms^-1)
            beta: β速率常数 (ms^-1)
            
        Returns:
            稳态值 (无量纲)
        """
        if alpha + beta == 0:
            return 0.0
        return alpha / (alpha + beta)
    
    def _gate_tau(self, alpha: float, beta: float) -> float:
        """
        计算门控变量的时间常数
        
        Args:
            alpha: α速率常数 (ms^-1)
            beta: β速率常数 (ms^-1)
            
        Returns:
            时间常数 (ms)
        """
        if alpha + beta == 0:
            return 1.0  # 避免除以零
        return 1.0 / (alpha + beta)
    
    def _derivatives(self, V: float, m: float, h: float, n: float, t: float) -> Tuple[float, float, float, float]:
        """
        计算状态变量的导数 (dV/dt, dm/dt, dh/dt, dn/dt)
        
        Args:
            V: 膜电位 (mV)
            m: 钠通道激活门
            h: 钠通道失活门
            n: 钾通道激活门
            t: 当前时间 (ms)
            
        Returns:
            dV/dt, dm/dt, dh/dt, dn/dt
        """
        # 获取当前外部电流
        I_ext = self.I_ext_func(t)
        
        # 计算门控变量的α和β
        alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n = self._alpha_beta(V)
        
        # 计算离子电流
        I_Na = self.g_Na 互动 (m神经元节点3) 互动 h 互动 (V - self.E_Na)  # 钠电流
        I_K = self.g_K 互动 (n神经元节点4) 互动 (V - self.E_K)         # 钾电流
        I_L = self.g_L 互动 (V - self.E_L)                  # 漏电流
        
        # 膜电位导数 (dV/dt)
        dVdt = (I_ext - I_Na - I_K - I_L) / self.C_m
        
        # 门控变量导数
        dmdt = alpha_m 互动 (1.0 - m) - beta_m * m
        dhdt = alpha_h 互动 (1.0 - h) - beta_h * h
        dndt = alpha_n 互动 (1.0 - n) - beta_n * n
        
        return dVdt, dmdt, dhdt, dndt
    
    def _rk4_step(self) -> None:
        """
        执行一步RK4积分
        """
        # 当前状态
        V0, m0, h0, n0 = self.V, self.m, self.h, self.n
        t0 = self.t
        
        # RK4系数 k1
        k1_V, k1_m, k1_h, k1_n = self._derivatives(V0, m0, h0, n0, t0)
        
        # RK4系数 k2
        V_k2 = V0 + 0.5 * self.dt * k1_V
        m_k2 = m0 + 0.5 * self.dt * k1_m
        h_k2 = h0 + 0.5 * self.dt * k1_h
        n_k2 = n0 + 0.5 * self.dt * k1_n
        k2_V, k2_m, k2_h, k2_n = self._derivatives(V_k2, m_k2, h_k2, n_k2, t0 + 0.5 * self.dt)
        
        # RK4系数 k3
        V_k3 = V0 + 0.5 * self.dt * k2_V
        m_k3 = m0 + 0.5 * self.dt * k2_m
        h_k3 = h0 + 0.5 * self.dt * k2_h
        n_k3 = n0 + 0.5 * self.dt * k2_n
        k3_V, k3_m, k3_h, k3_n = self._derivatives(V_k3, m_k3, h_k3, n_k3, t0 + 0.5 * self.dt)
        
        # RK4系数 k4
        V_k4 = V0 + self.dt * k3_V
        m_k4 = m0 + self.dt * k3_m
        h_k4 = h0 + self.dt * k3_h
        n_k4 = n0 + self.dt * k3_n
        k4_V, k4_m, k4_h, k4_n = self._derivatives(V_k4, m_k4, h_k4, n_k4, t0 + self.dt)
        
        # 更新状态
        self.V = V0 + (self.dt / 6.0) 互动 (k1_V + 2互动k2_V + 2互动k3_V + k4_V)
        self.m = m0 + (self.dt / 6.0) 互动 (k1_m + 2互动k2_m + 2互动k3_m + k4_m)
        self.h = h0 + (self.dt / 6.0) 互动 (k1_h + 2互动k2_h + 2互动k3_h + k4_h)
        self.n = n0 + (self.dt / 6.0) 互动 (k1_n + 2互动k2_n + 2互动k3_n + k4_n)
        
        # 更新时间
        self.t += self.dt
        
        # 确保门控变量在[0,1]范围内
        self.m = max(0.0, min(1.0, self.m))
        self.h = max(0.0, min(1.0, self.h))
        self.n = max(0.0, min(1.0, self.n))
    
    def _record_state(self) -> None:
        """记录当前状态到历史"""
        self.V_history.append(self.V)
        self.m_history.append(self.m)
        self.h_history.append(self.h)
        self.n_history.append(self.n)
        self.I_ext_history.append(self.I_ext_func(self.t))
        self.time_history.append(self.t)
    
    def step(self) -> None:
        """
        执行一步仿真并记录状态
        """
        self._rk4_step()
        self._record_state()
    
    def simulate(self, duration: float, 
                 I_ext_func: Optional[Callable[[float], float]] = None) -> None:
        """
        仿真指定时长
        
        Args:
            duration: 仿真时长 (ms)
            I_ext_func: 可选的外部电流函数，会覆盖当前设置
        """
        if I_ext_func is not None:
            self.I_ext_func = I_ext_func
        
        # 计算步数
        steps = int(duration / self.dt)
        
        # 执行仿真
        for _ in range(steps):
            self.step()
    
    def reset(self, V: Optional[float] = None, 
              m: Optional[float] = None,
              h: Optional[float] = None,
              n: Optional[float] = None,
              t: Optional[float] = None) -> None:
        """
        重置神经元状态
        
        Args:
            V: 膜电位 (mV)，默认使用静息电位
            m: 钠通道激活门，默认使用静息值
            h: 钠通道失活门，默认使用静息值
            n: 钾通道激活门，默认使用静息值
            t: 时间，默认重置为0
        """
        self.V = V if V is not None else -65.0
        self.m = m if m is not None else 0.0529
        self.h = h if h is not None else 0.5961
        self.n = n if n is not None else 0.3177
        self.t = t if t is not None else 0.0
        
        # 清空历史
        self.V_history = []
        self.m_history = []
        self.h_history = []
        self.n_history = []
        self.I_ext_history = []
        self.time_history = []
        
        # 记录初始状态
        self._record_state()
    
    def get_state(self) -> dict:
        """
        获取当前状态
        
        Returns:
            包含所有状态变量的字典
        """
        return {
            'V': self.V,
            'm': self.m,
            'h': self.h,
            'n': self.n,
            't': self.t,
            'I_ext': self.I_ext_func(self.t)
        }
    
    def get_history(self) -> dict:
        """
        获取仿真历史
        
        Returns:
            包含所有历史记录的字典
        """
        return {
            'time': np.array(self.time_history),
            'V': np.array(self.V_history),
            'm': np.array(self.m_history),
            'h': np.array(self.h_history),
            'n': np.array(self.n_history),
            'I_ext': np.array(self.I_ext_history)
        }
    
    def get_spike_times(self, threshold: float = 0.0) -> np.ndarray:
        """
        检测动作电位发生时间
        
        Args:
            threshold: 检测阈值 (mV)，默认0mV
            
        Returns:
            动作电位发生时间的数组 (ms)
        """
        if len(self.V_history) < 2:
            return np.array([])
        
        V = np.array(self.V_history)
        time = np.array(self.time_history)
        
        # 找到V超过阈值的点
        above_threshold = V > threshold
        
        # 找到上升沿（从低于阈值到高于阈值的转变）
        rising_edges = np.where(np.diff(above_threshold.astype(int)) == 1)[0]
        
        # 返回对应的时间
        return time[rising_edges]
    
    def get_firing_rate(self, threshold: float = 0.0) -> float:
        """
        计算平均发放频率
        
        Args:
            threshold: 检测阈值 (mV)
            
        Returns:
            平均发放频率 (Hz)
        """
        spike_times = self.get_spike_times(threshold)
        
        if len(spike_times) < 2:
            return 0.0
        
        # 计算平均发放频率
        total_time = self.time_history[-1] - self.time_history[0]
        if total_time <= 0:
            return 0.0
        
        # 转换到Hz (1000 ms = 1 s)
        return 1000.0 * len(spike_times) / total_time


# 辅助函数：生成常用刺激模式
def create_pulse_train(pulse_amp: float, pulse_duration: float, 
                       interval: float, total_duration: float) -> Callable[[float], float]:
    """
    创建脉冲序列刺激
    
    Args:
        pulse_amp: 脉冲幅度 (μA/cm²)
        pulse_duration: 脉冲持续时间 (ms)
        interval: 脉冲间隔 (ms)
        total_duration: 总时长 (ms)
        
    Returns:
        返回电流函数 I_ext(t)
    """
    def I_ext(t):
        if t < 0 or t > total_duration:
            return 0.0
        
        # 计算当前脉冲周期
        cycle_time = t % (pulse_duration + interval)
        
        if cycle_time < pulse_duration:
            return pulse_amp
        else:
            return 0.0
    
    return I_ext


def create_constant_current(I_const: float) -> Callable[[float], float]:
    """
    创建恒定电流刺激
    
    Args:
        I_const: 恒定电流 (μA/cm²)
        
    Returns:
        返回电流函数 I_ext(t)
    """
    return lambda t: I_const


def create_ramp_current(I_start: float, I_end: float, 
                        ramp_duration: float) -> Callable[[float], float]:
    """
    创建斜坡电流刺激
    
    Args:
        I_start: 起始电流 (μA/cm²)
        I_end: 结束电流 (μA/cm²)
        ramp_duration: 斜坡持续时间 (ms)
        
    Returns:
        返回电流函数 I_ext(t)
    """
    def I_ext(t):
        if t < 0:
            return I_start
        elif t > ramp_duration:
            return I_end
        else:
            # 线性互动值
            return I_start + (I_end - I_start) 互动 (t / ramp_duration)
    
    return I_ext


def create_semantic_pressure_current(semantic_intensity: float, 
                                     baseline: float = 0.0,
                                     gain: float = 10.0) -> Callable[[float], float]:
    """
    将语义压力转换为电流刺激
    
    示例：将情感强度、欲望压力、惩罚信号等语义输入
    转换为神经元的电生理刺激
    
    Args:
        semantic_intensity: 语义强度 (0-1或任意标度)
        baseline: 基线电流 (μA/cm²)
        gain: 增益系数，控制强度到电流的转换比例
        
    Returns:
        返回电流函数 I_ext(t)（恒定值，但可扩展为时变）
    """
    # 简单线性映射：语义强度 → 电流
    current = baseline + gain * semantic_intensity
    
    # 返回恒定电流函数
    return lambda t: current


def create_chemosensory_signal(concentration_profile: Callable[[float], float],
                               sensitivity: float = 5.0,
                               adaptation_rate: float = 0.01) -> Callable[[float], float]:
    """
    模拟化学感官信号输入
    
    化学物质浓度随时间变化 → 神经元电流刺激
    包含简单的适应机制
    
    Args:
        concentration_profile: 浓度函数 C(t) → 浓度值
        sensitivity: 敏感度系数
        adaptation_rate: 适应速率 (ms^-1)
        
    Returns:
        返回电流函数 I_ext(t)，包含适应效应
    """
    # 状态变量（在闭包内维护）
    adapted_level = 0.0
    last_t = 0.0
    
    def I_ext(t):
        nonlocal adapted_level, last_t
        
        # 计算时间差
        dt = t - last_t if last_t > 0 else 0.01
        last_t = t
        
        # 获取当前浓度
        concentration = concentration_profile(t)
        
        # 计算原始信号
        raw_signal = sensitivity * concentration
        
        # 应用适应（指数衰减）
        adapted_level = adapted_level + adaptation_rate 互动 (raw_signal - adapted_level) 互动 dt
        
        # 适应后的信号作为电流
        return adapted_level
    
    return I_ext


# 测试函数
def test_hh_neuron():
    """测试HH神经元的完整功能"""
    print("测试Hodgkin-Huxley神经元模型...")
    
    # 创建神经元
    neuron = HHNeuron(dt=0.01)  # 0.01ms步长
    
    # 测试1：静息状态
    print("\n1. 静息状态测试")
    print(f"初始膜电位: {neuron.V:.2f} mV")
    print(f"初始门控变量: m={neuron.m:.4f}, h={neuron.h:.4f}, n={neuron.n:.4f}")
    
    # 测试2：恒定电流刺激
    print("\n2. 恒定电流刺激测试")
    neuron.reset()
    neuron.set_I_ext_constant(10.0)  # 10 μA/cm²
    neuron.simulate(50.0)  # 仿真50ms
    
    history = neuron.get_history()
    print(f"仿真时长: {history['time'][-1]:.1f} ms")
    print(f"最终膜电位: {neuron.V:.2f} mV")
    
    # 测试3：脉冲序列刺激
    print("\n3. 脉冲序列刺激测试")
    neuron.reset()
    
    # 创建脉冲序列：10μA/cm²，2ms脉冲，10ms间隔，总共100ms
    pulse_train = create_pulse_train(
        pulse_amp=15.0,
        pulse_duration=2.0,
        interval=10.0,
        total_duration=100.0
    )
    
    neuron.set_I_ext(pulse_train)
    neuron.simulate(100.0)
    
    spike_times = neuron.get_spike_times(threshold=0.0)
    firing_rate = neuron.get_firing_rate(threshold=0.0)
    
    print(f"检测到 {len(spike_times)} 个动作电位")
    print(f"发放时间: {spike_times}")
    print(f"平均发放频率: {firing_rate:.2f} Hz")
    
    # 测试4：状态获取
    print("\n4. 状态获取测试")
    state = neuron.get_state()
    print(f"当前状态:")
    for key, value in state.items():
        if key != 't':
            print(f"  {key}: {value:.4f}")
    
    print("\n测试完成！")
    
    return neuron


if __name__ == "__main__":
    # 运行测试
    neuron = test_hh_neuron()
    
    # 可选：绘制结果
    try:
        import matplotlib.pyplot as plt
        
        history = neuron.get_history()
        
        fig, axes = plt.subplots(3, 1, figsize=(10, 8))
        
        # 绘制膜电位
        axes[0].plot(history['time'], history['V'], 'b-', linewidth=2)
        axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[0].set_ylabel('膜电位 (mV)')
        axes[0].set_title('Hodgkin-Huxley神经元响应')
        axes[0].grid(True, alpha=0.3)
        
        # 绘制门控变量
        axes[1].plot(history['time'], history['m'], 'r-', label='m (钠激活)')
        axes[1].plot(history['time'], history['h'], 'g-', label='h (钠失活)')
        axes[1].plot(history['time'], history['n'], 'b-', label='n (钾激活)')
        axes[1].set_ylabel('门控变量')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # 绘制外部电流
        axes[2].plot(history['time'], history['I_ext'], 'k-', linewidth=2)
        axes[2].set_xlabel('时间 (ms)')
        axes[2].set_ylabel('外部电流 (μA/cm²)')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Matplotlib未安装，跳过绘图。")
        print("要安装: pip install matplotlib")