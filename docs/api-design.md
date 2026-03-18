# 一键出行智能体 - API 设计文档

## API 概览

本文档定义了一键出行智能体系统的所有 API 端点。

### API Base URL

- **开发环境**: `http://localhost:8000/api/v1`
- **生产环境**: `https://api.yijianchuxing.com/api/v1`

### 通用约定

#### 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

#### 响应格式

所有 API 响应都采用以下 JSON 格式：

```json
{
  "success": boolean,
  "message": string,
  "data": any,
  "timestamp": string,
  "request_id": string
}
```

---

## 第一步：意图解析 API

### 1. 意图解析

#### 端点

```
POST /parse-intent
```

#### 描述

通过自然语言输入解析用户的出行意图，提取关键参数并自动补全缺失信息。

#### 请求体

```json
{
  "user_input": "string (required)",
  "user_id": "string (optional)",
  "context": "object (optional)"
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|-----|------|------|------|
| `user_input` | string | ✅ | 用户的自然语言输入，如："帮我规划3月20号从北京到大理的自驾游" |
| `user_id` | string | ❌ | 用户唯一标识，用于记录和追踪 |
| `context` | object | ❌ | 对话上下文，用于多轮对话中保持上下文 |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/parse-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000",
    "user_id": "user_123"
  }'
```

#### 响应体

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
    "travelers": [],
    "transport_mode": "self-driving",
    "budget_per_person": 2000.0,
    "preferences": {},
    "hotel_needed": true,
    "ticket_needed": true,
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

**响应字段说明**:

| 字段 | 类型 | 说明 |
|-----|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 人类可读的消息 |
| `intent` | object | 解析出的出行意图 (见下表) |
| `auto_filled_fields` | array | 自动补全的字段列表 |
| `suggestions` | array | 系统给出的建议 |
| `next_step` | string | 推荐的下一步操作 |

**intent 对象字段**:

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `intent_type` | string | 意图类型 | "travel_planning", "ticket_booking" |
| `confidence` | float | 识别置信度 (0-1) | 0.85 |
| `origin` | string | 出发地 | "北京" |
| `destination` | string | 目的地 | "大理" |
| `departure_date` | string | 出发日期 (YYYY-MM-DD) | "2025-03-20" |
| `departure_time` | string | 出发时间 (HH:MM) | "09:00" |
| `return_date` | string | 返回日期 (YYYY-MM-DD) | "2025-03-22" |
| `return_time` | string | 返回时间 (HH:MM) | "17:00" |
| `duration_days` | integer | 行程总天数 | 3 |
| `person_count` | integer | 出行人数 | 2 |
| `travelers` | array | 出行人详细信息 | [] |
| `transport_mode` | string | 交通方式 | "self-driving", "flight", "train", "bus" |
| `budget_per_person` | float | 人均预算 | 2000.0 |
| `preferences` | object | 其他偏好设置 | {} |
| `hotel_needed` | boolean | 是否需要酒店 | true |
| `ticket_needed` | boolean | 是否需要景区门票 | true |
| `auto_filled_fields` | array | 自动补全的字段 | ["person_count", "departure_time"] |

#### 可能的错误响应

```json
{
  "success": false,
  "message": "无法理解用户需求，请提供更清晰的描述",
  "intent": null,
  "suggestions": [
    "🔍 需要确认出发地",
    "🔍 需要确认目的地",
    "💡 请提供更多细节信息"
  ],
  "next_step": "请用户进一步说明需求"
}
```

#### 业务逻辑

1. **接收请求** → 记录用户输入
2. **LLM 调用** → 使用 Kimi 进行自然语言理解
3. **参数提取** → 从 LLM 响应中提取结构化数据
4. **验证 & 补全** → 验证提取的数据，补全缺失信息
5. **置信度评分** → 计算识别的可信度
6. **返回响应** → 返回结构化的意图对象

#### 特殊处理规则

- 如果未提供出发日期，系统不会自动填充，而是建议用户提供
- 如果提供了出发日期和行程天数，自动计算返回日期
- 如果置信度低于 0.7，返回警告建议
- 自动补全的字段 (如默认人数、时间) 会记录在 `auto_filled_fields` 中

---

## 健康检查 API

### 1. 服务健康检查

#### 端点

```
GET /health
```

#### 描述

检查后端服务和相关依赖的健康状态。

#### 请求示例

```bash
curl "http://localhost:8000/api/v1/health"
```

#### 响应

```json
{
  "status": "healthy",
  "service": "travel-planning",
  "kimi_configured": true,
  "timestamp": "2025-03-18T10:30:00Z"
}
```

---

## 测试 API

### 1. Kimi 连接测试

#### 端点

```
GET /test-kimi
```

#### 描述

测试 Kimi LLM 的连接和配置是否正常。

#### 请求示例

```bash
curl "http://localhost:8000/api/v1/test-kimi"
```

#### 成功响应

```json
{
  "status": "success",
  "message": "✓ Kimi API 连接正常",
  "model": "kimi-2.5",
  "response_preview": "你好，我是由 Moonshot AI 开发的..."
}
```

#### 失败响应

```json
{
  "status": "error",
  "message": "配置错误: Kimi API Key 未配置",
  "hint": "请检查 .env 文件中是否设置了 KIMI_API_KEY"
}
```

---

## 预留的 API (第二步及以后)

### 数据查询 API (Step 2)

```
POST /query-weather           # 查询天气信息
POST /query-traffic           # 查询交通方案
POST /query-hotels            # 查询酒店
POST /query-attractions       # 查询景区信息
```

### 行程规划 API (Step 3)

```
POST /generate-itinerary      # 生成行程方案
POST /validate-itinerary      # 验证行程冲突
POST /compare-plans           # 对比多个方案
```

### 用户交互 API (Step 4)

```
POST /confirm-itinerary       # 用户确认行程
POST /adjust-itinerary        # 微调行程
POST /add-more-details        # 补充更多信息
```

### 订单管理 API (Step 5)

```
POST /create-order            # 创建订单
GET  /orders                  # 获取订单列表
GET  /orders/{order_id}       # 获取订单详情
POST /update-order            # 更新订单
POST /cancel-order            # 取消订单
```

### 实时服务 API (Step 6)

```
GET  /trip/{trip_id}/status   # 获取行程实时状态
POST /emergency-help          # 紧急求助
POST /update-reminder         # 更新提醒设置
```

---

## 数据类型定义

### TravelIntent

```java
{
  intent_type: String,              // "travel_planning", "ticket_booking", etc.
  confidence: Double,               // 0.0 - 1.0
  origin: String,                   // 出发地地名
  destination: String,              // 目的地地名
  departure_date: String,           // ISO 8601 格式 (YYYY-MM-DD)
  departure_time: String,           // HH:MM 格式
  return_date: String,              // ISO 8601 格式 (YYYY-MM-DD)
  return_time: String,              // HH:MM 格式
  duration_days: Integer,           // 总天数
  person_count: Integer,            // 出行人数
  travelers: List<Traveler>,        // 出行人详细信息
  transport_mode: String,           // 交通方式
  budget_per_person: Double,        // 人均预算
  preferences: Map<String, Any>,    // 其他偏好
  hotel_needed: Boolean,            // 是否需要酒店
  ticket_needed: Boolean,           // 是否需要门票
  auto_filled_fields: List<String>, // 自动补全的字段列表
  raw_input: String                 // 原始用户输入
}
```

### Traveler

```java
{
  name: String,           // 出行人姓名
  id_number: String,      // 身份证号
  phone: String,          // 手机号
  age: Integer            // 年龄
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "message": "人类可读的错误信息",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `INVALID_INPUT` | 400 | 输入参数无效 |
| `MISSING_API_KEY` | 401 | API Key 未配置 |
| `LLM_ERROR` | 500 | LLM 调用失败 |
| `PARSE_ERROR` | 500 | 数据解析失败 |
| `RATE_LIMITED` | 429 | 请求超限 |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 |

---

## 速率限制

当前 MVP 版本暂无速率限制。

生产环境建议的限制：
- 同一用户：100 requests/hour
- 同一 IP：1000 requests/hour

---

## 认证 (待实现)

当前版本暂无认证机制。

未来版本将支持：
- Bearer Token 认证
- OAuth 2.0
- API Key 认证

---

## 版本历史

### v0.1.0 (2025-03-18)
- ✅ 实现意图解析 API
- ✅ 健康检查 API
- ✅ 测试 API

### 计划的版本

#### v0.2.0 (计划)
- 数据查询 API
- 行程规划 API

#### v0.3.0 (计划)
- 用户交互 API
- 订单管理 API

#### v1.0.0 (计划)
- 完整的行程管理系统
- 认证和授权
- 支付集成

---

## 开发工具

### Swagger/OpenAPI 文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### 测试工具

#### curl

```bash
curl -X POST "http://localhost:8000/api/v1/parse-intent" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"你的输入"}'
```

#### 
Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/parse-intent",
        json={"user_input": "你的输入"}
    )
    print(response.json())
```

#### JavaScript

```javascript
fetch('http://localhost:8000/api/v1/parse-intent', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({user_input: "你的输入"})
})
.then(r => r.json())
.then(data => console.log(data))
```

---

## 最佳实践

1. **总是检查 success 字段** → 判断请求是否成功
2. **处理自动补全字段** → 展示给用户哪些字段被自动填充
3. **关注置信度** → 置信度低于 0.7 时建议用户确认
4. **遵循建议** → 系统提供的 `suggestions` 和 `next_step` 指导用户下一步操作
5. **记录 request_id** → 便于问题排查

---

**API 文档最后更新**: 2025-03-18  
**版本**: 0.1.0
