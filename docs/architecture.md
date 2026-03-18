# 一键出行智能体系统 - 技术架构文档

> **核心愿景**: 通过AI技术，将复杂的出行规划流程简化为一句话就能完成

## 📋 目录

1. [系统架构](#系统架构)
2. [核心模块详解](#核心模块详解)
3. [API 文档](#api-文档)
4. [数据模型](#数据模型)
5. [开发指南](#开发指南)
6. [测试](#测试)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   前端交互层 (Web/App)                    │
│          语音/文本输入 → 行程卡片展示 → 用户中心          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP API
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Gateway                         │
│    路由 → 认证 → 速率限制 → 请求分发                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
    ┌────────────────────────────────────────────┐
    │      核心能力层 (LangChain + Kimi)         │
    │                                            │
    │  Step 1: NLU                              │
    │  ├─ 意图识别                               │
    │  ├─ 参数提取                               │
    │  └─ 默认值补全                             │
    │                                            │
    │  Step 2: 数据查询框架                      │
    │  ├─ 天气 API                              │
    │  ├─ 交通 API                              │
    │  ├─ 酒店 API                              │
    │  └─ 景区 API                              │
    │                                            │
    │  Step 3: 行程规划引擎                      │
    │  ├─ 方案生成                               │
    │  ├─ 冲突检测                               │
    │  └─ 多方案对比                             │
    │                                            │
    │  Step 4-7: 执行 & 管理                     │
    └────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
    ┌─────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
    │  数据库   │ │ 缓存   │ │ 消息队列 │ │ 文件存储 │
    └─────────┘ └────────┘ └──────────┘ └─────────┘
```

---

## 核心模块详解

### 1️⃣ 意图解析模块 (NLU)

**文件位置**: `app/core/nlu/__init__.py`

**功能**：
- 自然语言理解和意图识别
- 关键参数提取（地点、时间、人数、预算等）
- 缺失参数的智能补全
- 置信度评分

**核心类**: `TravelNLUProcessor`

```python
# 使用示例
from app.core.nlu import parse_travel_intent

result = await parse_travel_intent("帮我规划3月20号从北京到大理的自驾游")

if result.success:
    intent = result.travel_intent
    print(f"出发地: {intent.origin}")
    print(f"目的地: {intent.destination}")
    print(f"自动补全字段: {intent.auto_filled_fields}")
```

**输出数据结构**:

```python
TravelIntent(
    intent_type: str,           # "travel_planning"
    confidence: float,          # 0.85
    origin: str,                # "北京"
    destination: str,           # "大理"
    departure_date: str,        # "2025-03-20"
    departure_time: str,        # "09:00"
    return_date: str,           # "2025-03-22"
    return_time: str,           # "17:00"
    duration_days: int,         # 3
    person_count: int,          # 2
    transport_mode: str,        # "self-driving"
    budget_per_person: float,   # 2000.0
    hotel_needed: bool,         # True
    ticket_needed: bool,        # True
    auto_filled_fields: list,   # ["person_count", "departure_time"]
)
```

### 2️⃣ LLM 集成模块

**文件位置**: `app/core/llm/__init__.py`

**功能**：
- Kimi LLM 初始化和管理
- API 请求处理
- 响应缓存（可选）

**配置**:
```python
# .env 文件
KIMI_API_KEY=your_api_key_here
KIMI_BASE_URL=https://api.moonshot.cn/v1
```

**Kimi API 说明**:
- Kimi 兼容 OpenAI API 接口
- 使用 ChatOpenAI 进行初始化
- 模型名称: `kimi-2.5`

---

## API 文档

### POST /api/v1/parse-intent

**意图解析 - 第一步的核心接口**

#### 请求体
```json
{
  "user_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000",
  "user_id": "user_123",
  "context": {}
}
```

#### 响应
```json
{
  "success": true,
  "message": "✓ 意图识别成功 (置信度: 85%)",
  "intent": {
    "intent_type": "travel_planning",
    "confidence": 0.85,
    "origin": "北京",
    "destination": "大理",
    "departure_date": "2025-03-20",
    "departure_time": "09:00",
    "return_date": "2025-03-22",
    "return_time": "17:00",
    "duration_days": 3,
    "person_count": 2,
    "transport_mode": "self-driving",
    "budget_per_person": 2000.0,
    "auto_filled_fields": ["person_count", "departure_time", "return_time"],
    "raw_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"
  },
  "auto_filled_fields": ["person_count", "departure_time", "return_time"],
  "suggestions": [
    "✓ 将查询天气、交通、酒店等信息"
  ],
  "next_step": "进入第二步: 前置信息校验与多源数据查询"
}
```

### GET /api/v1/test-kimi

**测试 Kimi 连接**

#### 响应
```json
{
  "status": "success",
  "message": "✓ Kimi API 连接正常",
  "model": "kimi-2.5",
  "response_preview": "你好，我是由Moonshot AI开发的，名叫Kimi..."
}
```

### GET /api/v1/health

**健康检查**

```json
{
  "status": "healthy",
  "service": "travel-planning",
  "kimi_configured": true
}
```

---

## 数据模型

### TravelIntent

出行意图的结构化表示

| 字段 | 类型 | 说明 |
|-----|------|------|
| `intent_type` | str | 意图类型，如 "travel_planning" |
| `confidence` | float | 置信度 (0-1) |
| `origin` | str | 出发地 |
| `destination` | str | 目的地 |
| `departure_date` | str | 出发日期 (YYYY-MM-DD) |
| `departure_time` | str | 出发时间 (HH:MM) |
| `return_date` | str | 返回日期 (YYYY-MM-DD) |
| `return_time` | str | 返回时间 (HH:MM) |
| `duration_days` | int | 行程天数 |
| `person_count` | int | 出行人数 |
| `transport_mode` | str | 交通方式 |
| `budget_per_person` | float | 人均预算 |
| `preferences` | dict | 其他偏好 |
| `hotel_needed` | bool | 是否需要酒店 |
| `ticket_needed` | bool | 是否需要门票 |
| `auto_filled_fields` | list | 自动补全的字段 |
| `raw_input` | str | 原始用户输入 |

---

## 开发指南

### 环境设置

#### 1. 克隆或初始化项目

```bash
cd c:\一键出行\backend
```

#### 2. 创建 .env 文件

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入 Kimi API Key：

```
KIMI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx
ENVIRONMENT=development
```

获取 Kimi API Key：
1. 访问 https://console.moonshot.cn
2. 创建账户或登录
3. 创建 API Key
4. 复制到 .env 文件

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 运行初始化检查

```bash
python check_and_start.py
```

#### 5. 启动服务

```bash
python main.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 项目结构约定

```
backend/
├── app/
│   ├── core/                # 核心能力模块
│   │   ├── llm/            # LLM 集成
│   │   ├── nlu/            # 自然语言理解
│   │   ├── planner/        # 行程规划引擎 (待开发)
│   │   └── executor/       # 执行引擎 (待开发)
│   ├── api/                # API 端点
│   │   └── travel_planning.py
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑层 (待开发)
│   ├── tools/              # 工具接口层 (待开发)
│   ├── utils/              # 工具函数 (待开发)
│   └── config.py           # 配置管理
├── tests/                  # 单元测试
├── main.py                 # 应用入口
└── requirements.txt        # 依赖列表
```

### 添加新功能的步骤

1. **定义数据模型** → `app/models/`
2. **实现核心逻辑** → `app/core/`
3. **创建 API 端点** → `app/api/`
4. **编写单元测试** → `tests/`
5. **更新文档** → `docs/`

---

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试文件

```bash
pytest tests/test_nlu.py -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=app --cov-report=html
```

### 使用 API 文档进行测试

启动应用后，访问：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### 手动测试示例

```bash
# 测试意图解析
curl -X POST "http://localhost:8000/api/v1/parse-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "帮我规划3月20号从北京到大理的自驾游，3天，人均预算2000",
    "user_id": "test_user"
  }'

# 测试 Kimi 连接
curl "http://localhost:8000/api/v1/test-kimi"

# 健康检查
curl "http://localhost:8000/api/v1/health"
```

---

## 常见问题 (FAQ)

### Q: Kimi API Key 怎么获取？

A: 访问 https://console.moonshot.cn，注册账户后创建 API Key。

### Q: 为什么意图解析不准确？

A: 
- 确保用户输入足够清晰
- 可以调整 NLU 模块中的 temperature 参数
- 检查 Kimi 模型版本是否是最新的

### Q: 如何调整默认参数？

A: 在 `.env` 文件中修改：
```
DEFAULT_PERSON_COUNT=2
DEFAULT_DEPARTURE_TIME=09:00
DEFAULT_RETURN_TIME=17:00
```

### Q: 如何添加新的 API 接口？

A: 在 `app/api/travel_planning.py` 中添加新的路由函数，使用 `@router.get()` 或 `@router.post()` 装饰器。

---

## 下一步

- [ ] **Step 2**: 实现前置信息校验与多源数据查询框架
- [ ] **Step 3**: 开发行程规划引擎
- [ ] **Step 4**: 构建用户交互与微调接口
- [ ] **Step 5**: 实现订单管理服务
- [ ] **Step 6**: 开发实时服务与应急系统
- [ ] **Step 7**: 构建综合行程助手

---

**最后更新**: 2025-03-18  
**版本**: 0.1.0
