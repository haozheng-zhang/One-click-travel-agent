# 一键出行智能体 - 项目结构详解

## 文件树

```
一键出行/
│
├── backend/                          # 后端服务 (FastAPI + LangChain)
│   │
│   ├── app/                          # 应用代码
│   │   ├── __init__.py
│   │   ├── config.py                 # 全局配置管理
│   │   │
│   │   ├── core/                     # 核心能力层
│   │   │   ├── llm/
│   │   │   │   └── __init__.py       # Kimi LLM 集成 (第一步)
│   │   │   │       - KimiLLM 类
│   │   │   │       - get_llm() 函数
│   │   │   │
│   │   │   ├── nlu/
│   │   │   │   └── __init__.py       # NLU 意图解析模块 (第一步)
│   │   │   │       - TravelIntent 数据模型
│   │   │   │       - TravelNLUProcessor 类
│   │   │   │       - parse_travel_intent() 函数
│   │   │   │
│   │   │   ├── planner/              # 行程规划引擎 (待开发)
│   │   │   └── executor/             # 自动执行引擎 (待开发)
│   │   │
│   │   ├── api/                      # API 层
│   │   │   ├── __init__.py
│   │   │   └── travel_planning.py    # 旅行规划路由 (第一步)
│   │   │       - POST /parse-intent
│   │   │       - GET /test-kimi
│   │   │       - GET /health
│   │   │
│   │   ├── models/                   # 数据模型层
│   │   │   └── __init__.py           # Pydantic 数据模型
│   │   │       - UserProfile
│   │   │       - Traveler
│   │   │       - ItineraryCard
│   │   │
│   │   └── utils/                    # 工具函数
│   │       └── __init__.py
│   │           - parse_date()
│   │           - format_time()
│   │           - mask_sensitive_data()
│   │
│   ├── tests/                        # 测试代码
│   │   ├── __init__.py
│   │   └── test_nlu.py               # NLU 单元测试
│   │
│   ├── .env.example                  # 环境配置模板
│   ├── main.py                       # FastAPI 应用主入口
│   ├── start.py                      # 启动助手脚本
│   ├── check_and_start.py            # 启动前环境检查
│   ├── test_quick.py                 # 快速测试脚本 (无需启动服务)
│   └── requirements.txt              # Python 依赖列表
│
├── frontend/                         # Web 前端 (HTML + CSS + JS)
│   └── index.html                    # 单页应用
│       - 语音/文本输入框
│       - 结果展示面板
│       - 快速示例按钮
│       - 实时 API 调用
│
├── docs/                             # 文档目录
│   ├── architecture.md               # 🌟 系统架构详解 (必读)
│   ├── api-design.md                 # 🌟 API 完整文档 (开发必读)
│   ├── QUICKSTART.md                 # 🌟 快速开始指南 (新手必读)
│   └── user-flows.md                 # 用户流程 (规划中)
│
├── README.md                         # 项目总体说明
├── PROJECT_SUMMARY.md                # MVP 完成总结
└── PROJECT_GUIDE.md                  # 项目导览 (本文件)
```

---

## 核心模块说明

### 1. 配置系统 (`app/config.py`)

**职责**: 管理全局配置

**关键内容**:
- 环境变量加载
- 默认参数定义
- LLM 配置
- 日志配置

**使用方式**:
```python
from app.config import settings
print(settings.KIMI_API_KEY)
print(settings.DEFAULT_PERSON_COUNT)
```

### 2. LLM 集成 (`app/core/llm/__init__.py`)

**职责**: 初始化和管理 Kimi LLM

**关键类**:
- `KimiLLM` - 单例 LLM 管理器
- `get_llm()` - 便利函数获取 LLM 实例

**工作流程**:
```
应用启动 → 首次调用 get_llm() 
  → 初始化 ChatOpenAI(model="kimi-2.5")
  → 缓存实例供后续使用
```

### 3. NLU 模块 (`app/core/nlu/__init__.py`)

**职责**: 自然语言理解和意图解析

**关键类**:
- `TravelIntent` - 出行意图数据模型
- `TravelNLUProcessor` - 意图处理器
- `NLUResult` - 处理结果模型

**核心方法**:
```python
processor = TravelNLUProcessor()
result = await processor.process(user_input)
```

**处理流程**:
```
1. 准备提示词 (system + user)
2. 调用 Kimi LLM
3. 解析 JSON 响应
4. 后处理 (验证日期、补全信息)
5. 返回 NLUResult
```

### 4. API 路由 (`app/api/travel_planning.py`)

**职责**: 定义 HTTP 端点

**关键端点**:
```
POST /parse-intent    # 解析用户意图
GET  /test-kimi       # 测试 Kimi 连接
GET  /health          # 健康检查
```

### 5. 数据模型 (`app/models/__init__.py`)

**职责**: 定义 Pydantic 数据模型

**关键模型**:
- `UserProfile` - 用户信息
- `Traveler` - 出行人信息
- `ItineraryCard` - 行程卡片

---

## 请求流程示意

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP 请求                            │
│  POST /api/v1/parse-intent                              │
│  {"user_input": "..."}                                  │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              app/api/travel_planning.py                 │
│         parse_user_intent() 路由函数                    │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│          app/core/nlu/__init__.py                       │
│       TravelNLUProcessor.process()                      │
│  1. 准备 LangChain Prompt                               │
│  2. 调用 Kimi LLM                                       │
│  3. 解析 JSON 响应                                      │
│  4. 后处理数据                                          │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│        TravelIntent 结构化数据                          │
│  {                                                      │
│    "confidence": 0.85,                                  │
│    "origin": "北京",                                    │
│    "destination": "大理",                               │
│    ...                                                  │
│  }                                                      │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              PlanningResponse                           │
│        返回给客户端的 JSON 响应                          │
└─────────────────────────────────────────────────────────┘
```

---

## 代码调用路径

### 启动应用

```
main.py (FastAPI 入口)
    ├── 加载 .env 配置
    ├── 注册 CORS 中间件
    ├── 注册 API 路由
    │   └── include_router(travel_planning.router)
    └── 启动 Uvicorn 服务器
```

### 处理请求

```
POST /api/v1/parse-intent
    │
    └─→ app/api/travel_planning.py::parse_user_intent()
        │
        ├─→ from app.core.nlu import parse_travel_intent
        │
        └─→ app/core/nlu/__init__.py::parse_travel_intent()
            │
            └─→ TravelNLUProcessor().process()
                │
                ├─→ app/core/llm/__init__.py::get_llm()
                │   └─→ 初始化 ChatOpenAI(model="kimi-2.5")
                │
                └─→ LLM 处理
                    ├─→ 格式化提示词
                    ├─→ 调用 Kimi API
                    ├─→ 解析响应
                    └─→ 返回 TravelIntent
```

---

## 关键依赖说明

| 包 | 用途 | 文件 |
|----|------|------|
| `fastapi` | Web 框架 | main.py |
| `uvicorn` | ASGI 服务器 | main.py |
| `langchain` | LLM 编排框架 | app/core/nlu |
| `langchain-community` | LangChain 插件 | app/core/llm |
| `pydantic` | 数据验证 | app/models |
| `python-dotenv` | 环境变量 | app/config.py |
| `aiohttp` | 异步 HTTP | LangChain 内部使用 |
| `pytest` | 测试框架 | tests/ |

---

## 添加新功能的步骤

### 例子：添加景区查询功能

1. **创建数据模型** (`app/models/`)
   ```python
   class Attraction(BaseModel):
       name: str
       location: str
       hours: str
   ```

2. **创建工具模块** (`app/tools/attractions.py`)
   ```python
   async def query_attractions(city: str) -> List[Attraction]:
       # 调用景区 API
       pass
   ```

3. **集成到 NLU** (`app/core/nlu/__init__.py`)
   ```python
   # 在 TravelIntent 中添加
   attractions_needed: bool = False
   ```

4. **创建 API 端点** (`app/api/travel_planning.py`)
   ```python
   @router.post("/query-attractions")
   async def query_attractions(request: QueryRequest):
       # 处理请求
       pass
   ```

5. **编写测试** (`tests/test_attractions.py`)
   ```python
   async def test_query_attractions():
       # 测试逻辑
       pass
   ```

---

## 调试建议

### 查看 LLM 调用日志

```python
# 在 app/config.py 中开启
LANGCHAIN_VERBOSE = True
LANGCHAIN_DEBUG = True
```

### 使用断点调试

```python
# 在 test_quick.py 中添加
import pdb
pdb.set_trace()  # 在这里停止执行
```

### 查看 API 文档

```bash
# 启动后访问
http://localhost:8000/api/docs  (Swagger UI)
http://localhost:8000/api/redoc (ReDoc)
```

---

## 性能优化建议

### 缓存 LLM 响应

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def parse_travel_intent_cached(user_input: str):
    # 缓存相同话术的结果
    pass
```

### 使用异步处理

```python
# 后台任务记录日志
background_tasks.add_task(_log_intent, user_id, intent)
```

### 批量处理请求

```python
# 使用 Redis 缓存重复请求
redis_client.get(cache_key)
```

---

## 扩展点 (Extension Points)

### 1. 多语言支持

```python
# 在 app/core/nlu/__init__.py 中
class MultilingualNLU:
    def __init__(self, language: str):
        self.language = language
        self.system_prompt = self._get_prompt_for_language(language)
```

### 2. 多模型支持

```python
# 在 app/core/llm/__init__.py 中
class MultiModelLLM:
    def get_llm(self, model_name: str):
        if model_name == "kimi":
            return KimiLLM()
        elif model_name == "gpt":
            return GPT_LLM()
```

### 3. 自定义规则引擎

```python
# 在 app/core/nlu/__init__.py 中
class RulesEngine:
    def apply_custom_rules(self, intent: TravelIntent):
        # 应用自定义补全规则
        pass
```

---

## 常见修改

### 修改默认时间

```
文件: .env
修改: DEFAULT_DEPARTURE_TIME=10:00
```

### 修改 NLU 提示词

```
文件: app/core/nlu/__init__.py
方法: TravelNLUProcessor._setup_prompt_template()
```

### 添加新的 NLU 模式

```
文件: app/core/nlu/__init__.py
方法: TravelNLUProcessor._post_process_dates()
```

### 修改错误消息

```
文件: app/api/travel_planning.py
位置: PlanningResponse 的 message 字段
```

---

## 版本信息

| 组件 | 版本 | 更新时间 |
|-----|------|---------|
| 项目 | 0.1.0 | 2025-03-18 |
| FastAPI | 0.104.1 | - |
| LangChain | 0.1.1 | - |
| Python | 3.10+ | - |

---

**最后更新**: 2025-03-18  
**维护者**: 一键出行开发团队
