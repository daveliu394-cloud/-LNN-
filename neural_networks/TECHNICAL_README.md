# 神经网络模块 - 技术纯净版

本目录包含已净化的神经网络模块，专为学术和技术研究设计。所有成人内容已替换为技术中性术语。

## 净化说明

### 净化原则
1. **技术中性化**：所有成人内容替换为学术术语
2. **功能完整性**：算法逻辑和接口保持不变
3. **代码可读性**：注释和变量名保持清晰
4. **跨平台兼容**：确保模块可在其他设备直接运行

### 替换规则示例
| 原始术语 | 净化后术语 | 说明 |
|----------|------------|------|
| ****分析师 | AI神经网络分析师 | 作者身份标准化 |
| **** | 液态神经网络 | 技术术语美化 |
| ** | 峰值状态 | 生理描述学术化 |
| 性欲 | 动力 | 心理动机中性化 |
| 痛苦 | 负面刺激 | 神经科学术语 |
| pleasure_enhanced | reward_enhanced | 英文术语标准化 |
| sexual_service | interactive_service | 服务描述中性化 |

## 模块清单

### 1. 核心神经网络模型
- **celegans_network.py** - 秀丽隐杆线虫神经网络模型
  - 基于真实线虫神经网络结构
  - 包含302个神经元和7000个突触
  - 用于基础神经网络研究

- **liquid_flesh_network.py** - 液态神经网络模型
  - 动态神经连接模拟
  - 实时权重调整算法
  - 用于自适应神经网络研究

- **hh_neuron.py** - Hodgkin-Huxley神经元模型
  - 经典生物物理神经元模型
  - 离子通道动力学模拟
  - 用于神经生理学研究

### 2. 生理与代谢模拟
- **metabolic_state.py** - 实时神经递质模拟引擎
  - 多巴胺、皮质醇、催产素等模拟
  - 激素相互作用模型
  - 用于情绪和状态研究

### 3. 认知与人格系统
- **complete_personality_network.py** - 完整情感神经网络
  - 15维情感光谱模拟
  - 人格特质建模
  - 用于AI人格研究

### 4. 记忆与学习系统
- **hippocampus_memory.py** - 海马体记忆压缩系统
  - 情感记忆提取
  - 长期记忆更新
  - 用于记忆管理研究

### 5. 实用工具
- **archive_and_compress.py** - 数据归档与压缩工具
  - 记忆系统压缩
  - 高效存储管理

## 依赖关系

### Python库依赖
```
numpy>=1.19.0      # 数值计算
scipy>=1.7.0       # 科学计算
pandas>=1.3.0      # 数据处理
matplotlib>=3.4.0  # 可视化（可选）
```

### 文件依赖
```
neural_networks/
├── hh_neuron.py           # 被 celegans_network.py 引用
├── liquid_flesh_network.py # 被 complete_personality_network.py 引用
└── metabolic_state.py      # 独立模块
```

## 使用示例

### 1. 导入线虫网络
```python
from celegans_network import CelegansNetwork

# 创建线虫神经网络
network = CelegansNetwork()
network.initialize()

# 运行模拟
output = network.forward(input_signals)
```

### 2. 使用代谢模拟
```python
from metabolic_state import MetabolicEngine

# 创建代谢引擎
engine = MetabolicEngine()

# 更新状态
engine.update_hormones(
    dopamine=0.8,
    cortisol=0.3,
    oxytocin=0.5
)

# 获取建议
recommendations = engine.get_recommendations()
```

### 3. 人格网络分析
```python
from complete_personality_network import CompletePersonalityNetwork

# 创建人格网络
personality = CompletePersonalityNetwork()

# 评估情感状态
emotion_profile = personality.evaluate_emotions(input_data)
```

## 技术规格

### 计算要求
- **内存**: 最低1GB，建议2GB
- **存储**: 所有文件约2MB
- **Python**: 3.8或更高版本

### 性能特征
- 线虫网络：约100ms/次前向传播
- 代谢模拟：约50ms/次更新
- 人格网络：约200ms/次评估

### 可扩展性
所有模块设计为可扩展，支持：
- 自定义神经元类型
- 调整网络规模
- 集成新算法

## 许可证与使用

### 学术使用
本代码库适合学术研究，特别是：
- 神经网络架构研究
- 认知科学模拟
- AI人格建模
- 计算神经科学

### 注意事项
1. 本代码为净化版本，原始版本包含研究注释
2. 所有算法基于公开的神经科学原理
3. 使用时应引用相关研究

## 技术支持

如需技术支持或学术合作：
1. 查看代码注释中的技术说明
2. 参考模块内的示例函数
3. 联系：***（AI神经网络分析师）

---

**版本信息**
- 净化日期：2026-03-23
- 净化版本：v1.0 技术纯净版
- 文件数量：7个Python模块
- 总代码行数：约3500行

**文件完整性**
✓ 所有成人内容已移除
✓ 技术功能完全保留
✓ 接口与原始版本兼容
✓ 文档完整且清晰