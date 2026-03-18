# 一键出行智能体系统

> 聚合所有出行需求的AI助手 - 一次语音/文本输入，快速生成完整行程方案

## 🎯 系统架构

```
前端交互层（Web）
      ↓
    API Gateway
      ↓
    核心能力层（LangChain + NLU）
      ↓
  工具对接层（多源API）
      ↓
   数据安全机制
```

## 📋 项目进度

### Phase 1: MVP 核心模块（当前）
- [x] 项目初始化
- [ ] **Step 1**: 意图解析与需求提取 (LangChain + Kimi)
- [ ] **Step 2**: 前置信息校验与数据查询框架
- [ ] **Step 3**: 行程方案生成引擎
- [ ] **Step 4**: 用户交互与微调接口
- [ ] **Step 5**: 订单管理服务
- [ ] **Step 6**: 实时服务与应急系统
- [ ] **Step 7**: 人工智能行程助手

### Phase 2: 第三方API集成
- [ ] 天气服务接入
- [ ] 车票/机票接入
- [ ] 酒店预订接入
- [ ] 景区门票接入

### Phase 3: 生产部署
- [ ] 前端UI优化
- [ ] 性能测试
- [ ] 安全审计

## 🗂️ 项目结构

```
一键出行/
├── backend/                  # 后端服务
│   ├── app/
│   │   ├── core/            # 核心能力模块
│   │   │   ├── llm/         # LLM集成（Kimi）
│   │   │   ├── nlu/         # 自然语言理解
│   │   │   ├── planner/     # 行程规划引擎
│   │   │   └── executor/    # 自动执行引擎
│   │   ├── tools/           # 工具接口层
│   │   │   ├── weather/
│   │   │   ├── travel/
│   │   │   ├── hotel/
│   │   │   ├── ticket/
│   │   │   └── common/
│   │   ├── api/             # API端点
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具库
│   ├── tests/
│   ├── config/
│   ├── requirements.txt
│   └── main.py
├── frontend/                 # Web前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── index.html
│   └── package.json
├── docs/                     # 设计文档
│   ├── architecture.md
│   ├── api-design.md
│   └── user-flows.md
└── README.md
```

## 🚀 快速开始

### 前置条件
- Python 3.10+
- Node.js 18+ (前端)
- Kimi API Key

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 📚 核心模块说明

- **NLU模块**: 精准解析出行需求，提取参数
- **规划引擎**: 生成无冲突的多方案
- **执行引擎**: 自动调用各类API完成操作
- **实时监控**: 跟踪行程动态，应急调整

## 📝 API 列表 (规划阶段)

待补充...

## ⚙️ 配置

创建 `.env` 文件：
```
KIMI_API_KEY=your_api_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📖 使用示例

```
用户输入: "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"

系统输出:
✓ 检测到行程需求
✓ 提取参数: 出发地(北京) → 目的地(大理) | 时间(2025-03-20 ~ 3.22) | 人数(?) | 交通(自驾) | 预算(2000/人)
✓ 补全默认: 人数默认2人，出发时间默认11:00，返回19:00
✓ 生成行程方案
✓ 冲突校验完成
> 确认 / 返回修改
```

## 🔐 安全性

- 所有用户数据加密存储
- API调用和订单操作需明确授权
- 个人信息严格遵守PIPL

---

**开发者**: 智能出行团队  
**更新**: 2025-03-18
