# 一键出行智能体系统（One-click-travel-agent）

> 这是一个基于 LangGraph 架构开发的智能旅行规划 Agent。项目核心是通过 ReAct (Reasoning and Acting) 模式，将用户的模糊出行意图转化为结构化的旅行方案。

## 核心特性
- **ReAct** 循环架构：利用 LangGraph 显式构建推理-行动循环，相比于线性的 langChain，具备更强的逻辑容错与自我修正能力。

- 强类型状态管理：集成 Pydantic 进行 State 定义，通过自定义函数实现旅行意图（`TravelIntent`）的增量式合并，确保长对话链路中数据的一致性。

- 指令式状态更新 (Command Pattern)：工具节点通过返回 `Command` 对象直接操作 Graph 状态，实现了业务逻辑执行与状态演进的解耦。

- 数据提纯流水线：内置“搜索-解析-结构化”管道，能将非结构化的互联网搜索碎片提炼为强类型的 `WeatherReport` 和 `TravelIntentReport`。

你可以从 **`backend/app/core/graph.py`** 开始阅读源码，了解更多项目架构相关信息。

## 技术栈
- 框架: **LangChain / LangGraph**

- 测试模型: **deepseek v3.2**

- 数据源: **Tavily Search API**

- 校验: **Pydantic v2.10.0**

- 异步: **Asyncio v1.3.0**

阅读 **`requirements.txt`** 查看相关技术栈。

## 快速开始
### 1. 环境准备

```bash
git clone https://github.com/haozheng-zhang/One-click-travel-agent.git
cd One-click-travel-agent
# 这里可以创建Python虚拟环境：
# python -m venv .venv
# source .venv/bin/activate
pip install -r requirements.txt
```
### 2. 配置环境变量
在根目录下创建 .env 文件：
```bash
cp backend/.env.example backend/.env
```
打开`backend/.env`文件，填入你的API_KEY等信息：
```bash
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=your_llm_base_url_here # https://api.deepseek.com/v1
LLM_MODEL_NAME=your_model_name_here # deepseek-chat

TAVILY_API_KEY=your_key_here
```
### 3. 运行单元测试
```bash
pytest -s tests/test_graph.py # 也可以运行其他测试文件
```
可以更改测试文件内的输入以测试智能体对不同输入的反应。
## 当前进度
- 已配置好`docker`的基础设施。但要等实现前端等部分后才能实现一键打包运行。
- 前端的`vue`框架有待完善。
- 提示词有待完善。
- 工具的数量和功能性有待完善。

>更新:  `2025-03-25`
