# 一键出行智能体 - 项目导览

## 🎯 项目目标

开发一个**一键式出行智能体系统**，通过 AI 技术将复杂的出行规划流程简化为一句话就能完成。用户只需用自然语言描述出行需求，系统即可自动拆解、补全参数、生成行程方案、管理订单，最终实现全流程一键化。

---

## 📁 项目文件导览

### 核心目录结构

```
c:\一键出行\
│
├── 📂 backend/                      # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py               # ⚙️ 配置管理
│   │   │
│   │   ├── core/                   # 🧠 核心能力层
│   │   │   ├── llm/
│   │   │   │   └── __init__.py     # 🤖 Kimi LLM 集成
│   │   │   └── nlu/
│   │   │       └── __init__.py     # 💬 NLU 意图解析模块
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── travel_planning.py  # 🚀 旅行规划 API 端点
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py         # 📋 数据模型定义
│   │   │
│   │   └── utils/
│   │       └── __init__.py         # 🛠️ 工具函数
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_nlu.py             # ✅ NLU 单元测试
│   │
│   ├── .env.example                # 📝 环境配置示例
│   ├── main.py                     # ⚡ 应用入口
│   ├── start.py                    # 🚀 启动助手脚本
│   ├── check_and_start.py          # ✓ 启动前检查
│   ├── test_quick.py               # 🧪 快速测试脚本
│   └── requirements.txt            # 📦 依赖列表
│
├── 📂 frontend/
│   └── index.html                  # 🎨 Web UI 原型
│
├── 📂 docs/
│   ├── QUICKSTART.md               # 🚀 快速开始指南
│   ├── architecture.md             # 📐 系统架构详解
│   ├── api-design.md               # 📚 API 设计文档
│   └── user-flows.md               # 👥 用户流程 (待完成)
│
├── README.md                        # 📖 项目总述
└── PROJECT_SUMMARY.md              # 📊 完成总结
```

---

## 🚀 快速核查清单

- [x] ✅ **项目初始化** - 完整的目录结构
- [x] ✅ **配置系统** - .env 配置管理
- [x] ✅ **LLM 集成** - Kimi 模型接入
- [x] ✅ **NLU 模块** - 意图解析与参数提取
- [x] ✅ **API 服务** - FastAPI 框架和端点
- [x] ✅ **数据模型** - Pydantic 模型定义
- [x] ✅ **前端原型** - 现代化 Web UI
- [x] ✅ **测试框架** - 单元测试和快速测试
- [x] ✅ **文档完整** - 架构、API、快速开始文档
- [x] ✅ **启动脚本** - 便捷的启动工具

---

## 📖 文档导览

### 新手必读

1. **[快速开始](docs/QUICKSTART.md)** (5分钟)
   - 3分钟配置
   - 2分钟启动
   - 立即体验第一步功能

2. **[项目总结](PROJECT_SUMMARY.md)**
   - MVP 完成情况
   - 核心特性介绍
   - 发展规划

### 深度学习

3. **[系统架构](docs/architecture.md)**
   - 系统整体设计
   - 核心模块详解
   - 开发指南

4. **[API 文档](docs/api-design.md)**
   - 完整的 API 参考
   - 数据类型定义
   - 错误处理

### 项目概述

5. **[README](README.md)**
   - 项目简介
   - 核心目标
   - 技术栈

---

## 🎓 学习路径

### 第一阶段：入门（1小时）

```
1. 读 QUICKSTART.md (15分钟)
2. 配置 .env 文件 (5分钟)
3. 运行 python test_quick.py (10分钟)
4. 查看输出结果 (5分钟)
5. 访问 Swagger UI 测试 (10分钟)
   → 启动服务: python main.py
   → 访问: http://localhost:8000/api/docs
```

### 第二阶段：理解（2小时）

```
1. 阅读 PROJECT_SUMMARY.md (30分钟)
2. 查看 architecture.md (45分钟)
3. 浏览代码结构 (15分钟)
4. 理解 TravelIntent 数据模型 (30分钟)
```

### 第三阶段：开发（进行中）

```
1. 学习 api-design.md (45分钟)
2. 理解 NLU 模块实现 (1小时)
3. 开始定制开发 (持续)
```

---

## 🔧 常用命令

### 初始化

```bash
# 进入后端目录
cd c:\一键出行\backend

# 复制配置文件
cp .env.example .env

# 安装依赖
pip install -r requirements.txt
```

### 启动

```bash
# 启动助手（推荐）
python start.py

# 快速测试（无需服务）
python test_quick.py

# 启动完整服务
python main.py

# 启动前检查
python check_and_start.py
```

### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_nlu.py -v

# 查看测试覆盖率
pytest tests/ --cov=app --cov-report=html
```

### 开发

```bash
# 应用代码格式化
black app/

# 代码审计
flake8 app/

# 类型检查
mypy app/
```

---

## 💡 关键概念

### TravelIntent（出行意图）

系统的核心数据模型，包含：
- 地点信息：出发地、目的地
- 时间信息：出发日期、返回日期、出发时间、返回时间
- 人员信息：出行人数、出行人详情
- 偏好信息：交通方式、预算、特殊需求
- 元数据：置信度、自动补全字段、原始输入

### 意图解析流程

```
用户输入 (自然语言)
    ↓
LangChain + Kimi 处理
    ↓
参数提取与结构化
    ↓
验证与默认值补全
    ↓
置信度评分
    ↓
返回结构化的 TravelIntent
```

### 系统七个核心步骤

```
Step 1: 意图解析与需求提取 ✅ COMPLETED
Step 2: 前置信息校验与多源数据查询 ⏳ 规划中
Step 3: 行程方案生成与冲突校验 ⏳ 规划中
Step 4: 用户一键确认与灵活微调 ⏳ 规划中
Step 5: 订单统一管理与全节点提醒 ⏳ 规划中
Step 6: 行程中实时服务与应急调整 ⏳ 规划中
Step 7: 行程后收尾服务 ⏳ 规划中
```

---

## 🎯 使用场景示例

### 场景 1：简单出行规划

**用户输入**
```
"我想3月25号和朋友去杭州玩2天"
```

**系统处理**
```
✓ 识别出行意图
✓ 提取参数: 出发地(未指定), 目的地(杭州), 时间(3/25-3/26)
✓ 自动补全: 人数(2人), 出发时间(09:00), 返回时间(17:00)
```

**系统输出**
```json
{
  "success": true,
  "intent": {
    "destination": "杭州",
    "departure_date": "2025-03-25",
    "person_count": 2,
    "auto_filled_fields": ["person_count", "departure_time"]
  },
  "next_step": "进入第二步：查询天气、交通、酒店等信息"
}
```

### 场景 2：复杂多地出行

**用户输入**
```
"帮我规划云南环线：昆明→大理→丽江→泸沽湖，6天5晚，2个人，3000块钱一个人"
```

**系统处理**
```
✓ 识别多目的地行程
✓ 提取参数: 主要目的地(丽江), 天数(6), 人数(2), 预算(3000/人)
✓ 自动补全: 出发日期(最近下一个可行日期), 交通方式, 时间
```

---

## 🔗 与其他工具集成

### IDE / 编辑器
- VS Code - 点击打开工作区
- PyCharm - 导入为 Python 项目
- Jupyter - 使用 test_quick.py 进行交互式开发

### 测试工具
- Postman - 导入 OpenAPI JSON
- curl - 直接发送请求
- Python requests - 集成测试脚本

### LLM / API 平台
- Kimi Console - 管理 API Key 配额
- OpenAI API - 兼容接口（可替换）
- 其他 LLM - 可扩展支持

---

## ❓ 常见问题

### Q: 如何修改默认的人数、时间设置？

**A:** 编辑 `.env` 文件：
```
DEFAULT_PERSON_COUNT=3
DEFAULT_DEPARTURE_TIME=10:00
DEFAULT_RETURN_TIME=18:00
```

### Q: 系统支持多少种语言？

**A:** 当前仅支持中文。基于 LangChain 的架构能够轻松扩展至其他语言。

### Q: 如何自定义 NLU 提示词？

**A:** 编辑 `app/core/nlu/__init__.py` 中的 `_setup_prompt_template()` 方法。

### Q: 可以替换为其他 LLM 模型吗？

**A:** 可以。修改 `app/core/llm/__init__.py`，调用不同的 LLM 提供商。

### Q: 系统有速率限制吗？

**A:** 当前 MVP 无限制。生产环境建议添加速率限制中间件。

---

## 🚦 项目状态

### 当前版本：0.1.0 (MVP)

| 功能 | 状态 | 进度 |
|-----|------|------|
| Step 1: 意图解析 | ✅ 完成 | 100% |
| Step 2: 数据查询 | ⏳ 规划 | 0% |
| Step 3: 行程规划 | ⏳ 规划 | 0% |
| Step 4: 用户交互 | ⏳ 规划 | 0% |
| Step 5: 订单管理 | ⏳ 规划 | 0% |
| Step 6: 实时服务 | ⏳ 规划 | 0% |
| Step 7: 收尾服务 | ⏳ 规划 | 0% |

### 近期规划

- **v0.2.0** (4月) - 数据查询框架
- **v0.3.0** (5月) - 行程规划引擎
- **v1.0.0** (6月) - 生产级完整系统

---

## 📞 获取帮助

1. **查看文档** - 大多数问题都有答案
2. **查看日志** - 运行时的日志信息很有价值
3. **测试 Kimi 连接** - `GET /api/v1/test-kimi`
4. **查看示例代码** - `docs/` 目录中有完整示例

---

## 🎉 现在开始！

```bash
# 第一步：进入项目目录
cd c:\一键出行\backend

# 第二步：启动助手
python start.py

# 第三步：选择启动方式
# 选项 1：快速测试
# 选项 2：启动完整服务
# 选项 3：打开 Web UI
```

---

**祝你使用愉快！** 🚀

有任何问题，请查看相应的文档部分。

**创建时间**: 2025-03-18  
**最后更新**: 2025-03-18  
**版本**: 0.1.0
