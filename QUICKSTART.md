# 快速入门指南

## ⚡ 5分钟快速启动

### 第一步：配置环境

```bash
# 进入 backend 目录
cd backend

# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Deepseek API Key
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
```

### 第二步：构建docker镜像并启动

```bash
# 进入项目根目录
cd ..

#构建docker镜像并启动（前提是你已经安装好docker应用程序）
docker compose up --build
```

启动成功后，你会看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🧪 测试第一步 - 意图解析

### 方法 1：使用 API 文档 (Swagger UI)

1. 打开浏览器，访问 http://localhost:8000/api/docs
2. 找到 **POST /api/v1/parse-intent** 端点
3. 点击 "Try it out"
4. 输入示例数据：

```json
{
  "user_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000",
  "user_id": "test_user"
}
```

5. 点击 "Execute" 查看结果

### 方法 2：使用 curl

```bash
curl -X POST "http://localhost:8000/api/v1/parse-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000",
    "user_id": "test_user_1"
  }'
```

### 方法 3：使用 Python

```python
import asyncio
import httpx

async def test_intent_parsing():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/parse-intent",
            json={
                "user_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000",
                "user_id": "test_user_1"
            }
        )
        print(response.json())

asyncio.run(test_intent_parsing())
```

## 📊 预期输出

成功的响应应该看起来像这样：

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
    "transport_mode": "自驾",
    "budget_per_person": 2000.0,
    "hotel_needed": true,
    "ticket_needed": true,
    "auto_filled_fields": ["person_count", "departure_time", "return_time"],
    "raw_input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"
  },
  "auto_filled_fields": ["person_count", "departure_time", "return_time"],
  "suggestions": ["✓ 将查询天气、交通、酒店等信息"],
  "next_step": "进入第二步: 前置信息校验与多源数据查询"
}
```

## 🔍 关键观察点

1. **置信度** (confidence): 表示 AI 对意图识别的确信程度，0-1 范围，越接近 1 越准确
2. **自动补全字段** (auto_filled_fields): 显示系统根据默认规则自动补全的字段
3. **下一步建议** (next_step): 告诉你系统接下来应该做什么

## 🆘 故障排查

### 错误：Kimi API Key 未配置

```
❌ KIMI_API_KEY 未配置或使用了默认值
```

**解决方案**：
1. 编辑 `.env` 文件
2. 将 `KIMI_API_KEY=your_kimi_api_key_here` 改为实际的 API Key
3. 保存文件
4. 重新启动服务

### 错误：无法连接到 Kimi API

```
status: "error"
message: "连接失败: ..."
```

**解决方案**：
1. 检查网络连接
2. 验证 API Key 是否正确
3. 访问 https://console.moonshot.cn 检查 API 配额是否有限制
4. 检查防火墙设置

### 错误：Process exits without doing useful work

**解决方案**：
1. 确保在 `backend` 目录下运行 `python main.py`
2. 确保已安装所有依赖: `pip install -r requirements.txt`
3. 检查 Python 版本: `python --version` (需要 3.10+)

## 📝 测试用例

### 测试 1: 基础出行规划

```
输入: "我想去成都旅游，3月20号出发，3天"
预期: 意图识别成功，自动补全人数、出发时间等
```

### 测试 2: 详细信息提供

```
输入: "帮我规划一个从上海到杭州的周末短途，人数5人，包含酒店和景区票"
预期: 提取完整信息，置信度较高
```

### 测试 3: 模糊输入

```
输入: "我想出去玩"
预期: 识别为出行意图但置信度低，建议用户提供更多信息
```

## 🚀 下一步

成功完成第一步后，您可以：

1. 查看 [完整架构文档](docs/architecture.md) 了解整体设计
2. 开始实现第二步：数据查询框架
3. 根据需要调整 NLU 模块的参数

## 💡 提示

- 开发时推荐使用 Swagger UI (http://localhost:8000/api/docs)，可以直观感受 API
- 在日志中查看 LangChain 的详细处理过程
- 可以通过修改 `app/config.py` 中的 `DEFAULT_*` 参数来调整默认行为

---

**需要帮助？** 检查日志输出或查看 [完整文档](docs/architecture.md)
