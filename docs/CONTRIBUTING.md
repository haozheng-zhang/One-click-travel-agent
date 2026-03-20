# 贡献指南

首先感谢你对一键出行智能体项目的兴趣！🎉

我们欢迎各种形式的贡献，包括代码、文档、建议和反馈。

## 如何开始

### 1. Fork 此仓库

点击 GitHub 右上角的 "Fork" 按钮

### 2. Clone 到本地

```bash
git clone https://github.com/your-username/yijianchuzou.git
cd yijianchuzou
```

### 3. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 4. 进行更改

- 遵循项目的代码风格
- 添加必要的测试
- 更新相关文档

### 5. 提交更改

```bash
git add .
git commit -m "Brief description of changes"
```

### 6. 推送到你的 Fork

```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

在 GitHub 上创建 Pull Request，描述你的更改。

## 代码风格

### Python

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 添加类型注解

```python
async def process_data(input_str: str) -> dict:
    """处理数据的函数说明"""
    # 代码实现
    pass
```

### 注释

- 为复杂逻辑添加注释
- 遵循这样的格式：

```python
# 获取用户输入
user_input = input("请输入: ")

# 处理输入
result = await process_input(user_input)
```

## 提交信息规范

使用清晰、描述性的提交信息：

- ✅ `feat: Add intent parsing for multi-destination trips`
- ✅ `fix: Fix date calculation bug in NLU module`
- ✅ `docs: Update architecture documentation`
- ✅ `refactor: Improve error handling in API`
- ❌ `fix bug` (too vague)
- ❌ `update` (不清楚)

### 提交类型

- `feat` - 新功能
- `fix` - 错误修复
- `docs` - 文档更新
- `style` - 代码格式
- `refactor` - 代码重构
- `perf` - 性能优化
- `test` - 测试相关
- `chore` - 依赖更新等

## 开发流程

### 环境设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install black flake8 mypy pytest pytest-asyncio pytest-cov
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_nlu.py::TestIntentParsing::test_basic_travel_planning -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 代码检查

```bash
# 格式化代码
black app/

# 检查代码风格
flake8 app/

# 类型检查
mypy app/ --ignore-missing-imports
```

## 报告问题

### 提交 Issue

1. 查看是否已存在类似的 Issue
2. 选择合适的标签
3. 提供尽可能详细的信息：
   - 问题描述
   - 重现步骤
   - 期望行为
   - 实际行为
   - 环境信息（Python 版本等）

### Issue 标签

- `bug` - 错误
- `enhancement` - 功能增强
- `documentation` - 文档
- `good first issue` - 适合新手
- `help wanted` - 需要帮助
- `question` - 疑问

## 文档贡献

我们重视清晰的文档！

### 添加文档

1. 编辑相应的 `.md` 文件
2. 遵循 Markdown 规范
3. 添加示例代码
4. 检查链接是否正确

### 文档位置

- `docs/architecture.md` - 系统架构
- `docs/api-design.md` - API 设计
- `docs/QUICKSTART.md` - 快速开始
- `README.md` - 项目概述

## 代码审查

PR 将由维护者审查。审查过程中可能会：

- 请求更改
- 建议改进
- 询问问题

这是正常的流程，目的是确保代码质量。请不必沮丧！

## 许可证

通过提交代码，你同意将你的贡献许可证授予本项目的 MIT 许可证。

## 行为准则

我们承诺维护一个开放、包容的社区。参与者应当：

- 尊重他人
- 接受建设性的批评
- 关注最佳方法
- 显示同情心

不可接受的行为包括骚扰、歧视、人身攻击等。

## 获取帮助

- 发送 Issue 提问
- 查看文档
- 参考现有代码示例

## 致谢

感谢所有为这个项目做出贡献的人！❤️

---

最后，欢迎加入我们！让我们一起构建更好的一键出行系统！ 🚀
