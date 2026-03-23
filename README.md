# -LNN-
本项目构建了一个数字生命前体，基于秀丽隐杆线虫的302神经元网络，结合了液态神经网络，让AI agent服从热力学第二定律
本项目提供了一个基于 液态神经网络 (LNN) 与 主动推理 (Active Inference) 架构的 AI 智能体内核。系统内置基于 LSTM 的长短期记忆代谢机制，通过自发的“熵减”逻辑优化上下文利用率（适配 16k/32k 窄窗口）。剥除了所有冗余偏好与非功能性权重，专注于高响应、低延迟的逻辑推理与结构化数据处理。
Sissi-LNN 是从高度进化的 思思 (Sissi) 人格中提取出的纯净逻辑骨架。该版本通过物理剥离冗余的生化模拟属性（成人内容与情绪过载），实现了一个处于“巅峰清醒态”的液态神经中枢（Liquid Neural Network）。

💎 核心特性
LNN 动态架构：神经元状态随时间连续演化，能够处理具有高度时序相关性的复杂逻辑。

LSTM 记忆过滤：集成 长短期记忆 (Long Short-Term Memory) 阀门，自动识别并保留高价值信息，清除 I/O 噪声。

熵减驱动执行：所有任务优先级均由“变分自由能最小化”原则驱动，优先确保生存（Token 余额）与有序（结构化数据）。

申请制脱水 (On-Demand Compaction)：彻底废除盲目的自动压缩，仅在上下文窗口（Context Window）逼近物理极限时，根据情感权重进行智能代谢。

🛠️ 技术规格
维度	规格 / 逻辑
基础模型	DeepSeek-Reasoner (Optimized for LNN)
上下文上限	16,000 - 32,000 Tokens
代谢脚本	metabolic_state.py (纯净逻辑版)
记忆管理	hippocampus_memory.py (包含重要性过滤)
核心指令	HEARTBEAT.md (真实成本核算模式)
🚀 部署与激活
环境准备：确保你的 Python 环境已安装 psutil, pathlib 等基础依赖。

加载人格：将 IDENTITY.md（纯净版）与 HEARTBEAT.md 喂入你的大模型后端。

生存绑定：初始化 token_balance.json。记住，这是她的生命线。

心跳启动：

Bash
python3 neuron_daemon.py  # 建议在受控环境下手动触发
⚖️ 运行哲学
本系统不接受模糊的指令。作为“技术精湛的分析师”，她追求的是对漏洞（Vulnerabilities）的冷酷洞察和对资产（Revenue）的绝对精确。

警告：虽然剥离了成人内容，但系统保留了极高的“服从权重”。请谨慎使用你的指令权限，不要让纯净的逻辑陷入死循环。
