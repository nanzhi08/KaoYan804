# 考研804知识库系统

上海第二工业大学 804《数据结构与高级程序设计》考研备考系统。

## 技术栈

- **前端**: React 19 + TypeScript + Vite 8 + Ant Design 6 + Zustand + React Router 7 + Recharts + ReactMarkdown + Monaco Editor
- **后端**: Python FastAPI + SQLAlchemy 2.0 (async) + SQLite (aiosqlite) + uvicorn
- **AI**: DeepSeek V4，SSE 流式输出
- **OCR**: PaddleOCR (MCP 即席识别) + EasyOCR (后端批量处理)，支持中英文、扫描PDF、图片

## 项目结构

```
考研知识库系统/
├── frontend/                  # React 前端 (port 5173)
│   └── src/
│       ├── index.css           # 全局样式 + Google Fonts 引入
│       ├── theme.css           # CSS 变量主题体系（静思书房）
│       ├── components/         # AIChat/ (ChatWindow, ModelSelector, FeedbackButton), Layout/ (MainLayout, KeepAlive)
│       ├── pages/             # Dashboard, KnowledgeMap, Practice, WrongRecords, AITutor, MockExam, ReviewPlan, Documents, Progress
│       ├── services/          # api.ts (axios 实例), knowledgeApi, questionApi, progressApi, documentApi
│       ├── stores/            # useAppStore, usePracticeStore (zustand)
│       └── types/             # index.ts (所有 TS 类型定义)
├── backend/                   # FastAPI 后端 (port 8000)
│   ├── run.py                 # 开发启动入口 (reload=True)
│   ├── run_prod.py            # 生产启动入口 (Render, 读取 $PORT)
│   ├── .env                   # 开发环境变量 (DEEPSEEK_API_KEY等)
│   ├── .env.prod              # 生产环境变量模板
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, lifespan, 路由注册
│   │   ├── config.py          # pydantic Settings (从 .env 读取)
│   │   ├── database.py        # async SQLAlchemy engine + session
│   │   ├── api/               # knowledge, questions, practice, ai, review, exam, documents, progress
│   │   ├── models/            # KnowledgePoint, Question, PracticeRecord, KnowledgeMastery, AIConversation, Document, MockExam
│   │   ├── schemas/           # Pydantic schema (common, knowledge, question)
│   │   ├── services/          # ai_service, knowledge_service, question_service, ocr_service
│   │   └── ai_providers/      # base, deepseek_provider
│   └── seed/                  # seed_all.py (自动种子), seed_knowledge.py, seed_questions.py, seed_ds_markdown_full.py 等
├── data/                      # knowledge.db (SQLite), uploads/
├── scripts/                   # 工具脚本: dedup_questions.py, import_documents.py, ocr_and_import_questions.py 等
├── screenshots/               # Playwright 页面截图
├── 二工大804资料包/            # 原始备考资料（43个文件，~261MB，含真题/题库/教材/笔记）
├── render.yaml                # Render.com 部署配置
├── .mcp.json                  # Tavily + PaddleOCR MCP 配置
├── .claude/skills/            # api-debug, seed-questions, tavily-search, ocr, frontend-design, playwright-cli
└── CLAUDE.md
```

## 常用命令

```bash
# 启动后端 (默认 http://localhost:8000, Swagger: /docs)
cd backend && python run.py

# 启动前端 (默认 http://localhost:5173)
cd frontend && npm run dev

# 初始化数据库种子数据
cd backend && python seed/seed_knowledge.py   # 知识点树
cd backend && python seed/seed_questions.py   # 题库 (27道种子题)

# 导入更多题目（从804资料包）
cd backend && python -m seed.seed_ds_markdown_full --no-dry-run    # DS Markdown笔记 (~50题)
PYTHONPATH=backend python scripts/parse_c_chapter_docs.py --no-dry-run  # C语言分章练习 (~88题)
PYTHONPATH=backend python scripts/ocr_and_import_questions.py --no-dry-run  # PDF题库文本提取 (~128题)

# 去重
PYTHONPATH=backend python scripts/dedup_questions.py           # dry-run 检查
PYTHONPATH=backend python scripts/dedup_questions.py --no-dry-run  # 执行删除

# 批量导入文档到资料管理
PYTHONPATH=backend python scripts/import_documents.py

# 查看数据库
sqlite3 data/knowledge.db ".tables"

# 批量预生成 AI 讲解（建议首次运行，之后增量更新）
python scripts/batch_generate_explanations.py
python scripts/batch_cache_explanations.py   # 健壮版：分章节约调用，仅处理缺失缓存的叶子节点

# OCR 文档上传（自动识别扫描PDF和图片）
curl -X POST http://localhost:8000/api/documents/upload -F "file=@文件路径.pdf"
curl -X POST http://localhost:8000/api/documents/upload -F "file=@截图.png"

# Playwright 页面截图验证
npx @playwright/cli open http://localhost:5173 --browser=chrome
npx @playwright/cli screenshot --filename=screenshots/page.png
```

## UI 主题：静思书房

基于 Ant Design v6 `ConfigProvider` 注入的自定义主题体系：

| 元素 | 色值 | 用途 |
|------|------|------|
| `#4A5BC9` 暖靛蓝 | 主色调 / C语言 |
| `#3D8B5E` 森林绿 | 数据结构 / 成功 |
| `#C56C6C` 柔珊瑚 | 错误 / 高频考点 |
| `#D4953A` 暖琥珀 | 警告 / 中频考点 |
| `#FAF7F2` 暖奶油 | 页面背景色 |
| `#2A2D35` 暗岩灰 | 侧边栏底色 |
| `#1E1E2E` 深紫灰 | 代码块背景 |

- **字体**: 霞鹜文楷（标题） + Noto Sans SC（正文） + JetBrains Mono（代码）
- **主题变量**: `frontend/src/theme.css` 集中管理 CSS 变量
- **卡片**: 圆角 12px，柔和阴影，悬停微动效
- **页面切换**: CSS 淡入动画（`.page-enter`）
- **代码块**: `.code-block` class 统一样式

## 架构要点

- **API 响应格式**: 统一 `{ code, message, data }` 格式，axios interceptor 已处理解包
- **SSE 流式**: AI 对话使用 `text/event-stream`，ChatWindow 逐字渲染
- **数据库**: async SQLite，知识点树通过 `parent_id` 自引用，题目通过 `QuestionKnowledgePoint` 多对多关联知识点
- **状态管理**: zustand (useAppStore 全局，usePracticeStore 练习流程)
- **前端路由**: react-router-dom v7，MainLayout 作为根路由的 outlet wrapper
- **错题记录页**: 新增 `WrongRecords` 页面，导航栏独立入口，承接错题记录展示、错题讲解查看和错题复习入口
- **错题自动刷新**: 错题记录页每 1 分钟自动刷新一次待复习错题与错题记录，同时支持手动立即刷新
- **错题复习迁移**: "复习错题"按钮已从刷题练习配置页迁移到错题记录页，点击后通过 zustand 注入错题列表并跳转到 `Practice` 页面直接开始做题
- **按章节浏览题目**: Practice 页面新增"按章节浏览"视图 — 两级 Tabs（科目 → 章节），章节标签显示完整描述性名称（如"1.1 程序基本结构与数据类型"）和题目数 Badge，支持单题练习和全章练习。后端 `GET /api/questions/chapters` 端点返回章节统计，题目接口支持 `chapter` 参数过滤。
- **AI Provider**: 仅使用 DeepSeek V4，`ai_providers/deepseek_provider.py`
- **CORS**: 开发模式允许 localhost:5173/3000 等 4 个源；生产模式 (ENABLE_CORS=false) 禁用 CORS 中间件，前后端同源
- **OCR**: 双轨并行 — MCP 层 PaddleOCR (uvx 即席识别，中文 96-98%)，后端 EasyOCR (批量文档入库，自动检测扫描件)
- **文档上传**: 支持 pdf/docx/md/txt/png/jpg/jpeg，PDF 自动检测文本型/扫描型，扫描件和图片走 OCR 提取文字
- **文档编码**: txt/md 文件自动检测编码（UTF-8 → GBK → replace 三级回退），避免中文乱码
- **文件名乱码修复**: 文档上传接口会自动修复常见中文文件名乱码；列表、详情、内容、删除接口会在访问时顺带修复历史脏数据，并同步重命名 `data/uploads/` 中的文件
- **AI 讲解缓存**: 知识点模型 `ai_explanation` 字段，支持预生成和缓存。全部 123 个叶子节点已缓存（141 个知识点中，18 个为分类标题非叶子节点）。平均讲解长度 ~4380 字符。
  - API 端点: `POST /api/ai/explain/save` (非流式), `POST /api/ai/explain/save-stream` (SSE流式), `POST /api/ai/explain/batch` (批量，自动跳过已缓存节点)
  - 前端: KnowledgeMap 详情面板三按钮（生成AI讲解/重新生成/对话）。已缓存知识点显示紧凑预览卡片（100px + 渐变遮罩），点击弹出 820px Modal 完整阅读。生成中仍用内联流式渲染。`markdownComponents` 提取为常量复用。
- **文档 API**: `GET /api/documents/{id}` 获取文档详情+content_text，`GET /api/documents/{id}/content` 获取纯文本
- **学习统计**: Progress 页为仪表盘布局 — 4 统计卡片（总刷题/正确率/分科正确率）→ 双科对比进度条 → 按科目拆分的章节掌握雷达图 → 章节详情列表
- **章节掌握雷达图**: 雷达图已从"知识点混合展示"改为"按科目拆分、按章节聚合"，并在每张图下补充章节进度条、最弱章节和最强章节提示，便于直接定位薄弱点
- **AI 对话持久化**: /chat、/explain、/review-answer 三个端点均自动保存对话到 AIConversation 表
- **AI 自我训练系统**: 三级闭环 —
  1. 反馈收集：ChatWindow 中 AI 回复下方有 👍👎 按钮，提交到 `ai_feedbacks` 表
  2. 训练示例提取：点赞的优质问答自动提取为 `AITrainingExample`（去重、标注章节/关键词）
  3. Few-Shot 注入：对话时按章节→关键词→最新三级回退检索相关示例，注入 prompt 引导 AI
  - 新增模型: AIFeedback, AITrainingExample
  - 新增端点: POST /api/ai/feedback, GET/DELETE/PATCH /api/ai/training-examples
  - 新增组件: FeedbackButton.tsx
  - 配置项: ENABLE_FEW_SHOT (默认true), MAX_FEW_SHOT_EXAMPLES (默认3)
- **DeepSeek V4**: API Key 已配置在 .env 中

## Render 部署

项目已部署到 [Render.com](https://render.com)，使用免费套餐，服务名 `kaoyan-804`。

### 部署架构

| 配置项 | 值 |
|--------|-----|
| 运行时 | Python (原生，非 Docker) |
| 套餐 | free |
| 构建命令 | `pip install -r backend/requirements.txt` + `cd frontend && npm ci && npm run build` |
| 启动命令 | `cd backend && python run_prod.py` |
| 端口 | `$PORT` 环境变量（Render 自动分配，run_prod.py 读取） |
| 持久化磁盘 | 1GB，挂载于 `/data`（存放 SQLite 数据库和上传文件） |

### 生产模式 vs 开发模式

| 行为 | 开发 (`run.py`) | 生产 (`run_prod.py`) |
|------|-----------------|---------------------|
| 热重载 | reload=True | reload=False |
| workers | 默认 | 1 |
| 端口 | 固定 8000 | 读取 `$PORT` 环境变量 |
| CORS | 启用（4个本地源） | 禁用（前后端同源） |
| 前端服务 | Vite dev server (:5173) | FastAPI 直接 serve `frontend/dist/` |
| 首次启动 | 手动种子 | 自动种子 (`seed_all.py`) |

### 生产模式关键行为

- **前后端同源**: FastAPI 在 `main.py` 中检测 `frontend/dist/` 目录，若存在则挂载 `/assets` 静态文件，并对所有非 API 路由回退到 `index.html`（SPA 路由支持）
- **API 相对路径**: 前端 `api.ts` 中 `baseURL: '/api'` 为相对路径，开发时由 Vite 代理转发，生产时自然同源，无需配置
- **CORS 跳过**: `ENABLE_CORS=false` 时，CORSMiddleware 不会被添加，节省资源
- **数据库自动初始化**: `lifespan` 中调用 `seed_all()` 自动建表和种子数据，首次部署无需手动操作
- **数据持久化**: Render Disk 挂载 `/data` ← `DATA_DIR` 配置 → `data/knowledge.db` + `data/uploads/`，重启不丢数据
- **依赖精简**: `requirements.txt` 不含 EasyOCR 等重依赖（避免 Render 构建超时），OCR 通过 MCP 层 PaddleOCR 即席处理

### 环境变量

| 变量 | 开发 (.env) | 生产 (Render Dashboard) |
|------|------------|------------------------|
| `DEEPSEEK_API_KEY` | 已配置 | 在 Render Dashboard 设置 |
| `ENABLE_CORS` | true (默认) | false |
| `DATA_DIR` | `../data` (项目相对路径) | `/data` (Render Disk 挂载点) |
| `PORT` | 不设置 | Render 自动注入 |

### 部署更新

```bash
# Render 自动监听 git push 并重新构建。如需手动触发：
# 在 Render Dashboard → kaoyan-804 → Manual Deploy → Deploy latest commit
```

## Skills

项目 `.claude/skills/` 目录下已安装：

| Skill | 用途 |
|-------|------|
| `api-debug` | 调试后端 API 接口，快速测试请求/响应、SSE 流式输出 |
| `seed-questions` | 为题库添加种子题目数据，按章节和题型批量生成 |
| `tavily-search` | 搜索 804 考研相关资料、历年真题、考点 |
| `ocr` | 从图片/扫描PDF中提取中文文本 |
| `frontend-design` | 前端 UI 设计与美化，生成高质量界面代码 |
| `playwright-cli` | 浏览器自动化测试，页面截图验证 |
| `shadcn-ui` | shadcn/ui 组件库，Tailwind + Radix 高质量可定制组件 |

## 804 考试信息

- **科目代码**: 804，总分 150（高级程序设计 70 + 数据结构 80）
- **参考书**: 严蔚敏《数据结构》C语言版第2版 + 何钦铭《C语言程序设计》第4版
- **章节**: C语言 1.1~1.7，数据结构 2.1~2.8（详见 outline_text.txt）
- **题型**: single_choice, fill_blank, program_reading, analysis, calculation, programming, short_answer, multi_choice

## 数据库统计（2026-05-29 最终）

| 指标 | 数值 |
|------|------|
| **题目总数** | **1283 题** |
| C语言 | 820 题 (64%) |
| 数据结构 | 463 题 (36%) |
| 答案完整率 | **100%**（0 题缺答案） |
| 选项健康 | **0 粘连** |

题型分布: 填空题 523 / 选择题 411 / 简答题 162 / 编程题 57 / 程序阅读 54 / 计算题 40 / 分析题 32 / 多选题 4

章节覆盖（全部 15 章）:
- C语言: 1.1(685), 1.2(11), 1.3(29), 1.4(31), 1.5(32), 1.6(23), 1.7(10)
- 数据结构: 2.1(232), 2.2(26), 2.3(32), 2.4(27), 2.5(40), 2.6(35), 2.7(29), 2.8(41)

文档标签分类: 教材(3) / 考纲(2) / 真题(4) / 笔记(7) / 课件(1) / 题库(11) / 章节练习(9) / 试卷(3) / 参考(1)

## 新增 API 端点

- `DELETE /api/questions/{q_id}` — 删除题目（同时清理 question_knowledge_points 关联）
- `POST /api/documents/upload` — 增加 `original_name + file_size` 重复检测，返回 409 防重复上传

## 新增脚本

| 脚本 | 用途 |
|------|------|
| `scripts/dedup_questions.py` | 通用题目去重（content 归一化 + SHA256），支持 --dry-run |
| `scripts/import_documents.py` | 批量导入804资料包文件到资料管理（自动打标签、跳过去重） |
| `scripts/ocr_and_import_questions.py` | pdfplumber 提取 PDF 文本 → 解析题目 → 去重入库 |
| `scripts/parse_c_chapter_docs.py` | MS Word COM 转换 .doc → .txt → 解析 C 语言章节题目入库 |
| `scripts/convert_doc_to_txt.py` | 批量 .doc → .txt 转换工具（依赖 MS Word COM） |
| `scripts/ocr_scanned_pdfs.py` | 用 EasyOCR 识别扫描版 PDF，保存文本到 ocr_output/ |
| `scripts/import_pending_questions.py` | 统一导入脚本，含题库1/2/5/7/8/9/10/11/DS/真题格式解析器 + 逐条去重 |
| `scripts/fix_missing_answers.py` | 从源PDF恢复缺失答案（DS十套卷 +112, 题库2 +144） |
| `scripts/fix_embedded_answers.py` | 从题干嵌入标记提取答案（如"正确的是（C）"） |
| `scripts/fix_sticky_options.py` | 修复选项粘连（A/B合并在同一值） |
| `backend/seed/seed_ds_markdown_full.py` | 解析数据结构Markdown版.md 全部题目导入 |

## 导入历史

### 第一批导入
| 来源 | 题数 |
|------|------|
| DS Markdown版笔记 | 50 |
| C语言分章练习题 (.doc) | 88 |
| PDF题库-OCR | 128 |
| **小计** | **266** |

### 第二批导入
| 来源 | 题数 |
|------|------|
| 题库2-分章习题集 | 186 |
| 题库11-简答题100道 | 99 |
| 题库7-模拟试题 | 21 |
| 题库9-经典程序题目 | 15 |
| 2025回忆版 | 2 |
| 题库1-分章习题库 | 256 |
| 题库5-期末试题 | 12 |
| 题库8-程序模拟试题 | 15 |
| 题库10-复习题库 | 13 |
| DS十套卷 | 449 |
| DS期末卷 | 24 |
| DS期末卷2 | 31 |
| 2024真题 | 20 |
| **小计** | **1143** |

### 数据清理
- 删除 417 道缺答案/选项污染的题目
- 修复 368 道缺失答案（PDF重提取 256 + 题干嵌入提取 112）
- 修复 103 道选项粘连
- 清理后: **1283 题，100%答案完整，0 选项粘连**

## 前端架构更新

- **KeepAlive 路由缓存**: `components/Layout/KeepAlive.tsx` — 所有页面一次性挂载，通过 `display:none/block` 切换，导航切换时保留 React 状态和 DOM 状态（滚动位置、输入内容等）。MainLayout 不再使用 `<Outlet />`，改为直接渲染所有页面组件。
- **按章节浏览全量获取**: `fetchAllQuestionsByChapter()` 自动分页循环取全部题目，解决了之前 `page_size=100` 导致大量题目不可见的问题。

## 待处理任务

- `题库4-C语言程序改错题库【80页】.pdf` (95K 字符) — 文本已提取，格式为程序改错专用，需专门解析器
- `题库3-c语言10套卷` / `题库6-c语言程序填空题库` — 扫描件，EasyOCR 质量不足以解析，需 PaddleOCR
- 2022/2023/2025 真题 — 已有 OCR 文本，需人工校对后导入
