# 考研804知识库系统 - Claude 工作指南

本项目是面向上海第二工业大学 804《数据结构与高级程序设计》的考研学习系统，围绕 804 专业课复习构建的本地学习平台，覆盖知识点、刷题、错题、AI 辅导、模拟考试、资料管理、OCR 和学习统计。

## 技术栈

- 前端：React 19 + TypeScript + Vite 8 + Ant Design 6 + Zustand + React Router 7 + Recharts + ReactMarkdown + Monaco Editor
- 后端：FastAPI + SQLAlchemy 2.0 async + SQLite/aiosqlite + Uvicorn + Pydantic Settings
- AI：DeepSeek + Claude Provider，SSE 流式输出，对话、讲解、答案点评、反馈训练样例
- 文档：PDF/图片/Markdown/Text/Docx 上传，后端文本提取与 OCR 服务
- MCP：Tavily、PaddleOCR、Git MCP

## 项目结构

`	ext
考研知识库系统/
├── frontend/                 React 前端工程
│   └── src/
│       ├── App.tsx           Ant Design 主题、路由入口
│       ├── components/       Layout(MainLayout/KeepAlive)、AIChat、MarkdownCode 等
│       ├── pages/            Dashboard、Study、Review、AITutor、AIHistory、MockExam、Documents
│       ├── services/         axios 实例与业务 API 封装 (api.ts, knowledgeApi, progressApi, systemApi)
│       ├── stores/           Zustand 状态 (useAppStore, usePracticeStore)
│       └── types/            TypeScript 类型定义
├── backend/                  FastAPI 后端工程
│   ├── run.py                开发启动入口 (reload=True)
│   ├── run_prod.py           Render 生产启动入口
│   ├── requirements.txt      后端依赖 (含 anthropic>=0.39)
│   ├── app/
│   │   ├── main.py           FastAPI app、CORS、lifespan、路由注册、SPA fallback
│   │   ├── config.py         环境配置 (Pydantic Settings v2, model_config)
│   │   ├── database.py       async SQLAlchemy engine/session/init_db + run_migrations
│   │   ├── migrations.py     轻量级迁移机制 (schema_migrations 表)
│   │   ├── time_utils.py     时间工具 (utc_now_naive 等)
│   │   ├── api/              knowledge/questions/practice/ai/review/exam/documents/progress
│   │   ├── models/           ORM 表模型 (11个表)
│   │   ├── schemas/          Pydantic schema (common/knowledge/question)
│   │   ├── services/         AI、知识点、题库、OCR、反馈服务
│   │   └── ai_providers/     base/deepseek_provider/claude_provider
│   ├── seed/                 自动种子数据与题库导入脚本
│   └── tests/                后端测试 (test_core_behaviors.py)
├── data/                     SQLite 数据库与上传文件
├── scripts/                  题库导入、去重、迁移等脚本
├── skills/                   已安装的 skills
├── docs/                     项目辅助文档
├── render.yaml               Render 部署配置
└── start.py                  本地一键启动脚本
`

## 导航结构（6项精简版）

当前导航为 6 项，通过 MainLayout 侧边栏 + React Router 懒加载实现：

| 导航项 | 路径 | 对应页面 | 包含功能 |
|--------|------|----------|----------|
| 学习仪表盘 | / | Dashboard | 今日概览、弱项章节、掌握度快览 |
| 学习中心 | /study | Study | 知识地图 + 刷题 + 错题 (Tab切换) |
| 复习进度 | /review | Review | 复习计划 + 学习统计 (Tab切换) |
| AI助手 | /ai-tutor | AITutor | AI对话 + 历史记录 (Tab切换) |
| 模拟考试 | /mock-exam | MockExam | 生成试卷、答题、提交 |
| 资料管理 | /documents | Documents | 上传、列表、查看、删除 |

## 常用命令

`powershell
# 一键启动前后端
python start.py

# 后端开发服务，默认 http://localhost:8000
cd backend
python run.py

# 前端开发服务，默认 http://localhost:5173
cd frontend
npm run dev

# 前端构建 (tsc -b && vite build)
cd frontend
npm run build

# 初始化或补充种子数据
cd backend
python seed/seed_all.py

# 数据库迁移检查
python scripts/migrate_db.py

# 题库导入和去重
python scripts/dedup_questions.py
python scripts/import_documents.py
`

## 前端架构要点

- App.tsx 只负责全局 Ant Design 中文 locale、主题 token（Indigo 色系）、React Router 入口。
- MainLayout 是页面容器，通过 KeepAlive 同时挂载所有页面，用 display: none/block 保留页面状态。
- 页面采用 React.lazy 懒加载，Vite 自动代码分割。
- services/api.ts 设置 aseURL: '/api'，开发态由 Vite proxy 转发到 127.0.0.1:8000，生产态由 FastAPI 同源服务。
- API 响应在 axios interceptor 中统一返回 
esponse.data。
- 状态管理使用 Zustand：useAppStore 全局选择状态，usePracticeStore 刷题流程状态。
- MarkdownCode 组件替代了 
eact-syntax-highlighter（已从依赖移除）。
- ite.config.ts 配置了 
olldownOptions.codeSplitting 分包策略（react-vendor, markdown-vendor）。

## 后端架构要点

- main.py 在 lifespan 中执行 init_db() → os.makedirs(uploads) → 自动 seed_all()。
- init_db() 内部：Base.metadata.create_all → 
un_migrations(conn)（迁移失败只记日志不阻断启动）。
- 路由模块（8个）：knowledge、questions、practice、ai、review、exam、documents、progress。
- config.py 使用 Pydantic v2 model_config = SettingsConfigDict(env_file=".env")，通过 DATA_DIR 生成 SQLite 路径。
- 数据库 SQLite async，核心表：
  - knowledge_points / questions / question_knowledge_points
  - practice_records / knowledge_mastery
  - documents / i_conversations / i_feedbacks / i_training_examples
  - mock_exams / schema_migrations
- AI 服务：聊天、知识点讲解（支持缓存到 DB）、答案点评、反馈收集、few-shot 训练样例。
- AI Provider：DeepSeek（默认，依赖 openai 包）和 Claude（按需懒加载，依赖 nthropic 包）。
- ClaudeProvider 采用懒加载（get_provider 函数内部 import），避免未安装 nthropic 时启动崩溃。
- 文档服务：上传保存到 data/uploads/，提取文本写入 DB。
- 迁移机制：migrations.py 管理 schema_migrations 表，	ime_utils.py 提供 UTC 时间工具。

## API 模块

- GET /api/health → {status, app, mode, user_label}
- /api/knowledge-points — 知识点树与详情
- /api/questions — 题目 CRUD、随机题、章节统计
- /api/practice — 提交答案、练习历史、错题、统计
- /api/ai — 聊天(SSE)、知识点讲解、讲解缓存、答案点评、反馈、训练样例
- /api/review — 待复习知识点、复习提交、复习统计
- /api/exam — 生成试卷、开始考试、提交、列表
- /api/documents — 上传、列表、详情、内容、删除
- /api/progress — 学习概览、章节详情、雷达图

## Render 部署

配置位于 
ender.yaml，使用 Python runtime：

- **构建**：pip install -r backend/requirements.txt → cd frontend && npm ci && npm run build
- **启动**：cd backend && python run_prod.py
- **环境变量**：PORT=8000，ENABLE_CORS=false
- **生产行为**：FastAPI 服务 rontend/dist，非 API 路由 fallback 到 index.html

### 常见部署问题速查

| 问题 | 原因 | 修复 |
|------|------|------|
| ModuleNotFoundError: No module named 'anthropic' | ClaudeProvider 顶层导入 | 已改为懒加载（292c900） |
| Exited with status 1 启动崩溃 | 
un_migrations 未捕获异常 | 已加 try/except（3ae069f） |
| 前端 502 Bad Gateway | 后端未启动或崩溃 | 检查 Render Logs 定位根因 |

## 开发约定

- 修改前先读相关文件，沿用现有目录、命名和业务分层。
- 前端新增 API 调用 → rontend/src/services/，类型 → rontend/src/types/。
- 后端新增接口 → 现有 pi/ 模块；复杂逻辑 → services/。
- ORM 表结构 → models/；接口入参/出参 → schemas/。
- 不要把 API Key、真实 token 写进文档或代码。
- 数据库和上传文件在 data/，操作前确认影响范围。
- AI Provider 新增时采用懒加载模式，避免缺少依赖时启动崩溃。

## 验证建议

- 后端改动：cd backend && python run.py 启动检查。
- 前端改动：cd frontend && npm run build 确保零错误。
- TypeScript：cd frontend && npx tsc --noEmit。
- 文档/配置：检查 Markdown 路径和命令是否与当前项目一致。

## 当前实现状态

- 导航已精简为 6 项：学习仪表盘、学习中心、复习进度、AI助手、模拟考试、资料管理。
- Study 页面通过 Tab 整合知识地图 + 刷题 + 错题。
- Review 页面通过 Tab 整合复习计划 + 学习统计。
- AITutor 页面通过 Tab 整合 AI 对话 + 历史记录。
- 后端已建立 schema_migrations 迁移机制和 	ime_utils 时间工具。
- 后端测试覆盖核心行为（题目筛选、判题、迁移表、AI Key 提示、健康检查）。
- ClaudeProvider 懒加载，nthropic 已加入 requirements.txt。
- 
eact-syntax-highlighter 已移除，改用自定义 MarkdownCode 组件。
- 单用户模式通过 APP_MODE/APP_USER_LABEL//api/health 暴露。

## 重要文档

- 项目架构书.md — 完整架构说明
- 项目详细说明书.md — 历史项目说明与业务背景
- 
ender.yaml — Render 部署配置
