# 考研804知识库系统 - Claude 工作指南

本项目是面向上海第二工业大学 804《数据结构与高级程序设计》的考研学习系统，围绕 804 专业课复习构建的本地学习平台，覆盖知识点、刷题、错题、AI 辅导、模拟考试、资料管理、OCR 和学习统计。

## 技术栈

- 前端：React 19 + TypeScript + Vite 8 + Ant Design 6 + Zustand + React Router 7 + Recharts + ReactMarkdown + Monaco Editor
- 后端：FastAPI + SQLAlchemy 2.0 async + SQLite/aiosqlite + Uvicorn + Pydantic Settings
- AI：DeepSeek + Claude Provider，SSE 流式输出，对话、讲解、答案点评、反馈训练样例
- 文档：PDF/图片/Markdown/Text/Docx 上传，后端文本提取与 OCR 服务
- MCP：Tavily、PaddleOCR、Git MCP

## 项目结构

`text
考研知识库系统/
├── frontend/                 React 前端工程
│   └── src/
│       ├── App.tsx           Ant Design 主题、路由入口
│       ├── components/       Layout(MainLayout/KeepAlive)、AIChat、MarkdownCode 等
│       ├── pages/            Dashboard、Study、Review、AITutor、MockExam、Documents、Login、Register、Admin
│       ├── services/         axios 实例与业务 API 封装 (api.ts, authApi, adminApi, knowledgeApi, questionApi, progressApi, documentApi, systemApi 等)
│       ├── stores/           Zustand 状态 (useAppStore, usePracticeStore, useAuthStore)
│       └── types/            TypeScript 类型定义
├── backend/                  FastAPI 后端工程
│   ├── run.py                开发启动入口 (reload=True，端口占用检测)
│   ├── run_prod.py           Render 生产启动入口 (reload=False)
│   ├── requirements.txt      后端依赖 (含 anthropic>=0.39, python-jose, passlib, bcrypt)
│   ├── app/
│   │   ├── main.py           FastAPI app、CORS、lifespan、路由注册、SPA fallback、Admin 自动创建
│   │   ├── config.py         环境配置 (Pydantic Settings v2, model_config)
│   │   ├── database.py       async SQLAlchemy engine/session/init_db + run_migrations
│   │   ├── migrations.py     轻量级迁移机制 (schema_migrations 表)
│   │   ├── time_utils.py     时间工具 (utc_now_naive 等)
│   │   ├── api/              knowledge/questions/practice/ai/review/exam/documents/progress/auth/admin (10个模块)
│   │   ├── models/           ORM 表模型 (13个表：users, invite_codes 新增)
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
└── start.py                  本地一键启动脚本（含端口自动清理）
`

## 导航结构

当前导航为 4 项核心功能 + 1 项管理员专属，通过 MainLayout 侧边栏 + React Router 懒加载实现。
Admin 页面已集成到 MainLayout 中（非独立页面），侧边栏在所有页面保持可见。

| 导航项 | 路径 | 对应页面 | 包含功能 |
|--------|------|----------|----------|
| 学习仪表盘 | / | Dashboard | 今日概览、弱项章节、掌握度快览 |
| 学习中心 | /study | Study | 知识地图 + 刷题 + 错题 (Tab切换) |
| 复习进度 | /review | Review | 复习计划 + 学习统计 (Tab切换) |
| 模拟考试 | /mock-exam | MockExam | 生成试卷、答题、提交 |
| 管理 (仅管理员) | /admin | Admin | 用户管理 + 邀请码生成 |

## 用户认证体系

系统已从单用户模式演进为多用户 JWT 认证：

- **注册**：需要有效邀请码（InviteCode 表），注册后邀请码标记为已使用
- **登录**：返回 JWT access_token，默认有效期 1440 分钟
- **角色**：user（普通用户）/ admin（管理员）
- **初始化**：首次启动自动创建 admin/admin123 管理员账户
- **前端守卫**：
  - AuthGuard：未登录重定向到 /login；Admin 页面访问控制通过 MainLayout 内 `isAdmin` 过滤实现
- **后端守卫**：
  - get_current_user：从 Authorization Bearer 解析 JWT，返回 User
  - require_admin：基于 get_current_user，验证 role == admin

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

- App.tsx 负责全局 Ant Design 中文 locale、主题 token（Indigo #6366F1 色系）、React Router 入口、AuthGuard/AdminGuard 认证守卫。
- MainLayout 是页面容器，通过 KeepAlive 同时挂载所有页面，用 display: none/block 保留页面状态。
- 页面采用 React.lazy 懒加载，Vite 自动代码分割。
- services/api.ts 设置 baseURL: '/api'，开发态由 Vite proxy 转发到 127.0.0.1:8000，生产态由 FastAPI 同源服务。
- API 响应拦截器：code=0/undefined 透传；非零业务码（401/400/409等）统一 reject 并保留服务端错误消息；HTTP 401 清除 token 并跳转登录页。
- Login/Register 页面错误处理兼容 axios error 和拦截器抛出的 Error 对象，正确展示服务端错误消息。
- 状态管理使用 Zustand：useAppStore 全局选择状态，usePracticeStore 刷题流程状态。
- MarkdownCode 组件替代了 react-syntax-highlighter（已从依赖移除）。
- vite.config.ts 配置了 rolldownOptions.codeSplitting 分包策略（react-vendor, markdown-vendor）。

## 后端架构要点

- main.py 在 lifespan 中执行 init_db() → 打印数据库状态 → os.makedirs(uploads) → seed_all() 自动创建 admin 账户。
- init_db() 内部：Base.metadata.create_all → run_migrations(conn)（迁移失败只记日志不阻断启动）。
- seed_all() 三级策略：①有知识点→跳过；②有用户但无知识点→ATTACH 种子库 INSERT OR IGNORE（保护用户数据）；③空库→copy2 初始化。
- 路由模块（10个）：knowledge、questions、practice、ai、review、exam、documents、progress、auth、admin。
- config.py 使用 Pydantic v2 model_config = SettingsConfigDict(env_file=".env")，通过 DATA_DIR 生成 SQLite 路径。新增 JWT_SECRET、JWT_ALGORITHM、JWT_EXPIRE_MINUTES、INIT_ADMIN_USERNAME、INIT_ADMIN_PASSWORD。
- dependencies.py：密码哈希/验证 (pbkdf2_sha256 为主，bcrypt 兼容已有密码)、JWT 签发/解析 (python-jose)、get_current_user、require_admin。
- 数据库 SQLite async，核心表：
  - knowledge_points / questions / question_knowledge_points
  - practice_records / knowledge_mastery
  - documents / ai_conversations / ai_feedbacks / ai_training_examples
  - mock_exams / schema_migrations
- AI 服务：聊天、知识点讲解（支持缓存到 DB）、答案点评、反馈收集、few-shot 训练样例。
- AI Provider：DeepSeek（默认，依赖 openai 包）和 Claude（按需懒加载，依赖 anthropic 包）。
- ClaudeProvider 采用懒加载（get_provider 函数内部 import），避免未安装 anthropic 时启动崩溃。
- 文档服务：上传保存到 data/uploads/，提取文本写入 DB。
- 迁移机制：migrations.py 管理 schema_migrations 表，time_utils.py 提供 UTC 时间工具。

## API 模块

- GET /api/health → {status, app, mode, user_label}
- /api/auth — 登录 (POST /login)、注册 (POST /register，需邀请码)
- /api/admin — 用户列表、删除用户、创建邀请码、邀请码列表 (Admin only)
- /api/knowledge-points — 知识点树与详情
- /api/questions — 题目 CRUD、随机题、章节统计
- /api/practice — 提交答案、练习历史、错题、统计
- /api/ai — 聊天(SSE)、知识点讲解、讲解缓存、答案点评、反馈、训练样例
- /api/review — 待复习知识点、复习提交、复习统计
- /api/exam — 生成试卷、开始考试、提交、列表
- /api/documents — 上传、列表、详情、内容、删除
- /api/progress — 学习概览、章节详情、雷达图

## Render 部署

配置位于 render.yaml，使用 Python runtime：

- **构建**：pip install -r backend/requirements.txt → cd frontend && npm ci && npm run build
- **启动**：cd backend && python run_prod.py
- **环境变量**：PORT=8000，ENABLE_CORS=false，DATA_DIR=/data，JWT_SECRET（生产务必修改）、DEEPSEEK_API_KEY、ANTHROPIC_API_KEY
- **生产行为**：FastAPI 服务 frontend/dist，非 API 路由 fallback 到 index.html

### 常见部署问题速查

| 问题 | 原因 | 修复 |
|------|------|------|
| ModuleNotFoundError: No module named 'anthropic' | ClaudeProvider 顶层导入 | 已改为懒加载（292c900） |
| Exited with status 1 启动崩溃 | run_migrations 未捕获异常 | 已加 try/except（3ae069f） |
| 前端 502 Bad Gateway | 后端未启动或端口被旧进程占用 | start.py 自动清理端口；run.py 检测提示 |
| 登录失败仅显示"登录失败" | 拦截器丢弃服务端错误消息 | 所有非零业务码 reject 并保留 message |
| JWT 验证失败 | JWT_SECRET 不匹配 | 确认生产 .env 中的 JWT_SECRET |
| 用户数据被清空 | seed_all 用 bundled DB 覆盖整个库 | 改为 ATTACH + INSERT OR IGNORE 仅导入种子表 |

## 开发约定

- 修改前先读相关文件，沿用现有目录、命名和业务分层。
- 认证逻辑集中在 dependencies.py，API 通过 Depends(get_current_user) / Depends(require_admin) 引入。
- 前端新增 API 调用 → frontend/src/services/，类型 → frontend/src/types/。
- 后端新增接口 → 现有 api/ 模块；复杂逻辑 → services/。
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

- 用户体系：JWT 认证 + bcrypt 密码哈希 + 邀请码注册 + 管理员后台。
- 导航：4 项核心功能（首页/学习/复习/模拟考试）+ 管理员专属（管理），Admin 页面已集成到 MainLayout。
- AI助手、资料库导航项已隐藏（后端 API 保留，可通过 URL 直接访问）。
- Study 页面通过 Tab 整合知识地图 + 刷题 + 错题。
- Review 页面通过 Tab 整合复习计划 + 学习统计。
- Admin 页面集成在 MainLayout 侧边栏内渲染，非管理员访问 /admin 自动重定向。
- 登录/注册页面：浅色动态背景（CSS 动画浮动 blob + 粒子光点），已移除学校名称。
- 后端 API 模块：10个（knowledge/questions/practice/ai/review/exam/documents/progress/auth/admin）。
- 数据库表：13个（users + invite_codes 新增，practice_records 加入 user_id）。
- 后端已建立 schema_migrations 迁移机制和 time_utils 时间工具。
- 后端测试覆盖核心行为（题目筛选、判题、迁移表、AI Key 提示、健康检查）。
- ClaudeProvider 懒加载，anthropic 已加入 requirements.txt。
- react-syntax-highlighter 已移除，改用自定义 MarkdownCode 组件。
- Vite 文件监听已排除 data/、backend/ 目录，防止数据库写入触发热重启。
- API 拦截器统一处理所有非零业务错误码，保留服务端 message 到前端错误提示。
- Login/Register 页面错误处理兼容 Error 对象，用户能看到具体失败原因（如"Invalid username or password"）。
- start.py 启动前自动清理端口 8000/5173 残留进程，消除 502 端口冲突。
- run.py 启动时检测端口占用，打印 taskkill 清理命令提示。
- seed_all 不再覆盖已有用户数据的数据库：有用户但无知识点时仅导入种子表，用户数据完整保留。
- main.py 启动时打印 `[Startup] DB at ...: N users, M knowledge points`，方便诊断 Render 磁盘异常。

## 重要文档

- 项目架构书.md — 完整架构说明
- 项目详细说明书.md — 历史项目说明与业务背景
- render.yaml — Render 部署配置
