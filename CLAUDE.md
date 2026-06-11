# 考研804知识库系统 - Claude 工作指南

本项目是面向上海第二工业大学 804《数据结构与高级程序设计》的考研学习系统。它不是通用知识库，而是围绕 804 专业课复习构建的本地学习平台，覆盖知识点、刷题、错题、AI 辅导、模拟考试、资料管理、OCR 和学习统计。

## 技术栈

- 前端：React 19 + TypeScript + Vite 8 + Ant Design 6 + Zustand + React Router 7 + Recharts + ReactMarkdown + Monaco Editor
- 后端：FastAPI + SQLAlchemy 2.0 async + SQLite/aiosqlite + Uvicorn + Pydantic Settings
- AI：DeepSeek Provider，SSE 流式输出，对话、讲解、答案点评、反馈训练样例
- 文档：PDF/图片/Markdown/Text/Docx 上传，后端文本提取与 OCR 服务
- MCP：Tavily、PaddleOCR、Git MCP；项目已提供 `/code-review` 命令封装 Git MCP 审查流程

## 项目结构

```text
考研知识库系统/
├── frontend/                 React 前端工程
│   └── src/
│       ├── App.tsx           Ant Design 主题、路由入口
│       ├── components/       Layout、AIChat 等复用组件
│       ├── pages/            Dashboard、KnowledgeMap、Practice、WrongRecords、ReviewPlan、Progress、AITutor、AIHistory、MockExam、Documents
│       ├── services/         axios 实例与业务 API 封装
│       ├── stores/           Zustand 状态
│       └── types/            TypeScript 类型
├── backend/                  FastAPI 后端工程
│   ├── run.py                开发启动入口
│   ├── run_prod.py           Render 生产启动入口
│   ├── app/
│   │   ├── main.py           FastAPI app、CORS、lifespan、路由注册、SPA fallback
│   │   ├── config.py         环境配置，生成 DATABASE_URL/UPLOAD_DIR
│   │   ├── database.py       async SQLAlchemy engine/session/init_db
│   │   ├── api/              knowledge/questions/practice/ai/review/exam/documents/progress
│   │   ├── models/           ORM 表模型
│   │   ├── schemas/          Pydantic schema
│   │   ├── services/         AI、知识点、题库、OCR、反馈服务
│   │   └── ai_providers/     base/deepseek_provider
│   └── seed/                 自动种子与题库导入脚本
├── data/                     SQLite 数据库与上传文件
├── scripts/                  题库导入、去重、OCR、AI 讲解缓存等脚本
├── skills/                   已安装的 Superpowers skills
├── .claude/                  Claude Code 本地配置、skills、slash commands
├── .mcp.json                 Claude Code 项目级 MCP 配置
├── .cursor/mcp.json          Cursor 项目级 MCP 配置
├── docs/MCP_CODE_REVIEW.md   MCP 代码审查说明
├── 项目架构书.md             项目架构说明
└── render.yaml               Render 部署配置
```

## 常用命令

```powershell
# 一键启动前后端
python start.py

# 后端开发服务，默认 http://localhost:8000
cd backend
python run.py

# 前端开发服务，默认 http://localhost:5173
cd frontend
npm run dev

# 前端构建
cd frontend
npm run build

# 初始化或补充种子数据
cd backend
python seed/seed_all.py
python seed/seed_knowledge.py
python seed/seed_questions.py

# 题库导入和清理
python scripts/dedup_questions.py
python scripts/import_documents.py
python scripts/batch_cache_explanations.py

# MCP 状态检查
claude mcp get git
claude mcp list
```

## 前端架构要点

- `frontend/src/App.tsx` 只负责全局 Ant Design 中文 locale、主题 token、React Router 入口。
- `MainLayout` 是实际页面容器；当前不使用嵌套路由 `<Outlet />`，而是通过 `KeepAlive` 同时挂载页面，使用 `display: none/block` 保留页面状态。
- 主菜单页面包括：学习仪表盘、知识地图、刷题练习、错题记录、复习计划、学习统计、AI 导师、历史回答、模拟考试、资料管理。
- `services/api.ts` 设置 `baseURL: '/api'`，开发态由 Vite proxy 转发到 `localhost:8000`，生产态由 FastAPI 同源服务。
- API 响应会在 axios interceptor 中统一返回 `response.data`，业务 service 中通常直接拿后端返回结构。
- 状态管理使用 Zustand：`useAppStore` 保存全局选择状态，`usePracticeStore` 保存刷题流程状态。

## 后端架构要点

- `backend/app/main.py` 在 lifespan 中执行 `init_db()`、创建上传目录，并尝试调用 `seed.seed_all.seed_all()` 自动补充基础数据。
- 路由模块按业务划分：知识点、题库、练习、AI、复习计划、模拟考试、文档、学习进度。
- `config.py` 通过 `DATA_DIR` 生成 SQLite 路径和上传目录；Render 生产环境使用 `/data` 挂载盘。
- 数据库是 SQLite async，核心表包括：
  - `knowledge_points`
  - `questions`
  - `question_knowledge_points`
  - `practice_records`
  - `knowledge_mastery`
  - `documents`
  - `ai_conversations`
  - `ai_feedbacks`
  - `ai_training_examples`
  - `mock_exams`
- AI 服务支持聊天、知识点讲解、讲解缓存、答案点评、反馈与 few-shot 训练样例。
- 文档服务保存上传文件到 `data/uploads/`，并把提取文本写入数据库。

## API 模块

- `GET /api/health`：健康检查
- `/api/knowledge-points`：知识点树与详情
- `/api/questions`：题目列表、随机题、章节统计、创建、删除
- `/api/practice`：提交答案、练习历史、错题、练习统计
- `/api/ai`：聊天、知识点讲解、讲解缓存、答案点评、反馈、训练样例
- `/api/review`：待复习知识点、复习提交、复习统计
- `/api/exam`：生成试卷、开始考试、提交试卷、考试列表
- `/api/documents`：上传、列表、详情、内容、删除
- `/api/progress`：学习概览、章节详情、雷达图数据

## MCP 与 Claude 命令

当前项目级 MCP：

- `tavily`：网络检索
- `paddleocr`：PaddleOCR 即席识别
- `git`：通过 `uvx mcp-server-git` 连接当前仓库，用于 diff、历史、文件上下文审查

已配置命令：

- `/code-review`：项目级代码审查命令，优先使用 `git` MCP。

可用方式：

```text
/code-review
/code-review current
/code-review staged
/code-review last
/code-review main..HEAD
/code-review frontend/src/App.tsx
```

MCP 详细说明见 `docs/MCP_CODE_REVIEW.md`。

## 开发约定

- 修改前先读相关文件，优先沿用现有目录、命名和业务分层。
- 前端新增 API 调用放到 `frontend/src/services/`，类型放到 `frontend/src/types/`。
- 后端新增接口优先按业务放入现有 `api/` 模块；复杂逻辑放入 `services/`，不要堆在路由函数里。
- ORM 表结构在 `models/` 中维护；接口入参/出参放 `schemas/`。
- 不要把 API Key、真实 token 写进文档或代码。`.mcp.json` 中已有本机配置，回答时不要泄露密钥。
- 数据库和上传文件位于 `data/`，执行清理、重建、删除前必须确认影响范围。
- Git MCP 需要 Claude Code、Git for Windows/Git Bash 和可执行的 `git.exe`。当前环境中 `git` 与 `claude` 不在 PATH，恢复后再运行 `/mcp` 或 `claude mcp list` 验证。

## 验证建议

- 后端改动：至少运行相关接口或 `python run.py` 启动检查。
- 前端改动：至少运行 `npm run build`；涉及 UI 时用浏览器或 Playwright 截图验证。
- 文档/配置改动：运行 `python -m json.tool` 校验 JSON；Markdown 需检查路径和命令是否仍与当前项目一致。
- MCP 改动：运行 `claude mcp get <server>` 或 `claude mcp list` 检查连接状态。

## 当前实现状态

- `ReviewPlan` 和 `Progress` 已挂入主导航，路径分别为 `/review-plan` 与 `/progress`。
- 后端已加入轻量级 `schema_migrations` 迁移记录机制，可用 `python scripts/migrate_db.py` 检查数据库状态。
- 导入、去重脚本会在 `data/import_reports/` 输出 JSON 导入报告。
- 当前运行环境中 `git` 和 `claude` 命令不在 PATH，`/code-review` 入口文件存在，但 Git MCP 依赖的 Claude Code + Git Bash/Git 环境需要先恢复。
- `.mcp.json` 仍包含本机 MCP 配置；外部服务密钥应改由环境变量注入，不应提交到远程仓库。

## 部署

项目使用 Render 部署，配置在 `render.yaml`：

- 构建：安装后端依赖，进入 `frontend` 执行 `npm ci && npm run build`
- 启动：`cd backend && python run_prod.py`
- 生产数据：`DATA_DIR=/data`
- 生产前端：FastAPI 服务 `frontend/dist` 并提供 SPA fallback

## 重要文档

- `项目架构书.md`：当前项目的完整架构说明
- `项目详细说明书.md`：历史项目说明与业务背景
- `docs/MCP_CODE_REVIEW.md`：MCP 代码审查配置说明
- `OCR识别效果展示报告.md`：OCR 识别效果记录
