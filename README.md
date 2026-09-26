# 简历投递助手

基于 Electron + Python FastAPI 的桌面应用，辅助在 BOSS 直聘上高效投递简历。集成看板管理、AI 智能回复、岗位收藏、数据统计等功能。

## 功能

- **投递看板** — 待投/已投/面试/已拒四列看板，支持拖拽更改状态、右键菜单快捷操作、搜索筛选
- **AI 回复助手** — 粘贴 HR 消息，AI 自动结合简历生成 3 个候选回复，可选正式/友好/简洁三种语气
- **岗位收藏** — 内置 webview 浏览 BOSS 直聘，一键提取岗位信息并创建投递记录
- **数据统计** — 总投递量、每日趋势柱状图、状态分布环形图、公司投递排行榜
- **模板管理** — 自定义常用话术模板，支持变量插入（{公司名}、{岗位名}、{姓名}）

## 快速开始

### 前置要求

- Node.js >= 18
- Python >= 3.10
- （可选）Ollama + qwen2.5:7b 用于本地 AI 回复
- （可选）OpenAI 兼容 API Key

### 安装与启动

```bash
# 1. 安装前端依赖
npm install

# 2. 安装后端依赖（使用清华镜像加速）
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 启动应用（自动启动后端 + Electron 窗口）
npm start
```

### 首次使用

1. 应用启动后，程序会自动打开主窗口
2. 点击左下角「设置」配置 AI 提供商（Ollama 或 OpenAI）
3. 在设置页面上传简历（支持 PDF / DOC / DOCX），AI 回复将自动参考简历内容
4. 开始创建投递记录或浏览 BOSS 直聘收藏岗位

## 项目结构

```
├── main.js                  # Electron 主进程
├── preload.js               # 预加载脚本（API 桥接）
├── package.json
├── frontend/
│   └── index.html           # 单页前端（Tailwind CSS + 原生 JS）
└── backend/
    ├── server.py            # FastAPI 后端服务（端口 5678）
    ├── db.py                # SQLite 数据库层（异步 aiosqlite）
    ├── ai.py                # AI 引擎（Ollama 优先，OpenAI 兼容 API 回退）
    ├── resume_parser.py     # 简历解析（PDF / DOCX）
    ├── test_db.py           # 数据库测试
    └── requirements.txt
```

## 技术栈

| 层级     | 技术                                          |
| -------- | --------------------------------------------- |
| 桌面壳   | Electron                                      |
| 前端     | 原生 HTML / Tailwind CSS / Font Awesome       |
| 后端     | Python FastAPI + uvicorn                      |
| 数据库   | SQLite + aiosqlite（WAL 模式）                 |
| AI 引擎  | Ollama（qwen2.5:7b） / OpenAI 兼容 API        |
| 简历解析 | PyPDF2 + python-docx                          |

## 配置

- **AI 提供商**: 支持 Ollama（默认）和 OpenAI 兼容 API，可在设置页面切换
- **AI 模型**: 默认使用 `qwen2.5:7b`（Ollama）或 `gpt-4o-mini`（OpenAI）
- **回复语气**: 正式、友好、简洁三种可选
- **后端端口**: 5678（硬编码，可通过修改 `backend/server.py` 调整）
- **数据库路径**: 可通过环境变量 `JOB_DB_PATH` 自定义

## 开发

```bash
# 单独启动后端（不启动 Electron）
python backend/server.py

# 后端运行在 http://127.0.0.1:5678
# 前端访问 http://127.0.0.1:5678 可查看 API 文档（FastAPI 自动生成）
```

## License

MIT
