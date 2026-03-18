# GitHub 发布步骤

> 🚀 将一键出行智能体项目推送到 GitHub

这个文件包含了完整的 GitHub 发布步骤。

## 前置条件

1. **安装 Git**
   - Windows: https://git-scm.com/download/win
   - 验证: `git --version`

2. **配置 Git**
   ```bash
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   ```

3. **创建 GitHub 账户**
   - 访问 https://github.com/join

4. **创建 Personal Access Token**
   - 转到 GitHub Settings → Developer settings → Personal access tokens
   - 创建新 token，勾选 `repo` 权限
   - 复制 token（待会儿会用到）

## 发布步骤

### 方法 1：使用现有 GitHub 仓库

```powershell
# 1. 进入项目目录
cd c:\一键出行

# 2. 初始化 git
git init

# 3. 添加远程仓库
git remote add origin https://github.com/yourusername/yijianchuzou.git

# 4. 添加所有文件
git add .

# 5. 创建首次提交
git commit -m "Initial commit: 一键出行智能体 MVP v0.1.0"

# 6. 推送到 GitHub（main 分支）
git branch -M main
git push -u origin main
```

### 方法 2：从零创建新仓库

**在 GitHub 上**：
1. 点击 "+" → "New repository"
2. 仓库名: `yijianchuzou`
3. 描述: `聚合所有出行需求的AI智能体系统`
4. 选择 "Public"（公开）
5. 添加 "Add .gitignore" → Python
6. 选择 "MIT License"
7. 创建仓库

**在本地**：
```powershell
# 进入项目目录
cd c:\一键出行

# 初始化 git
git init

# 创建首次提交
git add .
git commit -m "Initial commit: 一键出行智能体 MVP v0.1.0"

# 添加远程仓库（替换 yourusername）
git remote add origin https://github.com/yourusername/yijianchuzou.git

# 推送
git branch -M main
git push -u origin main
```

### 方法 3：使用 HTTPS 令牌认证（推荐）

```powershell
# 使用 token 替代密码
# 当要求输入密码时，粘贴你的 Personal Access Token

git remote set-url origin https://yourusername:your_personal_access_token@github.com/yourusername/yijianchuzou.git
```

### 方法 4：使用 SSH （更安全）

```powershell
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "你的邮箱"

# 添加到 SSH Agent
ssh-add ~/.ssh/id_ed25519

# 在 GitHub Settings → SSH and GPG keys → New SSH key
# 粘贴公钥内容 (cat ~/.ssh/id_ed25519.pub)

# 使用 SSH URL
git remote add origin git@github.com:yourusername/yijianchuzou.git
git push -u origin main
```

## 推送后的步骤

### 1. 添加 GitHub Topics（标签）
在仓库页面 → About → Topics
添加: `ai`, `travel`, `langchain`, `chatgpt`, `python`

### 2. 添加项目描述
在仓库页面 → Edit description
```
聚合所有出行需求的AI智能体系统。通过LangChain + Kimi实现自然语言理解，
一句话完成出行规划、行程生成、订单管理。MVP版本已完成第一步：意图解析与需求提取。
```

### 3. 创建 Release
```powershell
git tag -a v0.1.0 -m "Initial release: MVP version with intent parsing"
git push origin v0.1.0
```

然后在 GitHub 上转到 Releases → Create release from tag

### 4. 添加 GitHub Actions CI/CD（可选）

创建文件 `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v
```

## 常见问题

### Q: 怎样修改已推送的提交？

```powershell
# 修改最后一条提交
git commit --amend -m "新的提交信息"
git push -f origin main  # 强制推送（要谨慎！）
```

### Q: 怎样添加新分支？

```powershell
# 创建并切换到新分支
git checkout -b feature/new-feature

# 进行修改和提交
git add .
git commit -m "Add new feature"

# 推送分支
git push -u origin feature/new-feature

# 在 GitHub 上创建 Pull Request
```

### Q: 怎样同步本地和远程？

```powershell
# 获取最新版本
git fetch origin

# 合并远程变化
git merge origin/main

# 或一步到位
git pull origin main
```

### Q: 如何删除已推送的文件？

```powershell
# 从 Git 中删除但保留本地文件
git rm --cached filename

# 从 Git 和本地都删除
git rm filename

# 提交更改
git commit -m "Remove filename"
git push origin main
```

## 项目结构展示

推送后，GitHub 会自动显示项目结构。建议的布局：

```
yijianchuzou/
├── 📖 README.md              ← GitHub 主页
├── 📄 LICENSE                ← MIT 许可证
├── 📝 .gitignore             ← 忽略规则
│
├── 📂 backend/               ← 后端服务
│   ├── app/                  ← 应用代码
│   ├── tests/                ← 测试
│   ├── main.py
│   └── requirements.txt
│
├── 📂 frontend/              ← Web UI
│   └── index.html
│
├── 📂 docs/                  ← 文档
│   ├── QUICKSTART.md
│   ├── architecture.md
│   └── api-design.md
│
└── 📂 .github/               ← GitHub 配置
    └── workflows/            ← CI/CD
```

## 下一步

- [ ] 创建 GitHub 账户
- [ ] 创建新仓库
- [ ] 本地初始化 git
- [ ] 推送代码
- [ ] 添加 Topics 和描述
- [ ] 创建首个 Release
- [ ] 分享项目链接

## 有用的链接

- GitHub 指南: https://guides.github.com
- Git 命令参考: https://git-scm.com/docs
- GitHub CLI: https://cli.github.com/

---

**完成以上步骤后，你就可以在 GitHub 上分享这个项目了！** 🚀

示例仓库链接: `https://github.com/yourusername/yijianchuzou`
