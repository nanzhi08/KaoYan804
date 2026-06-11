# MCP code review setup

This project has an active Git MCP configuration for local repository review:

- Claude Code: `.mcp.json`
- Cursor: `.cursor/mcp.json`
- VS Code workspace MCP: `.vscode/mcp.json`

The enabled server is:

- `git`: starts with `uvx mcp-server-git --repository <project-root>`.

Other configured local MCP entries, such as Tavily, should read credentials from the user's environment. Do not commit API keys into project MCP JSON files.

The Git MCP server also needs a working Claude Code runtime, Git Bash on Windows, and a valid `git.exe`.

Current environment note: `git` and `claude` are not available in PATH in this workspace session, and Claude Code on Windows reports that Git Bash is required. The `/code-review` command file is present, but it cannot run MCP-backed review until Git for Windows/Git Bash and Claude Code are available to the shell.

The MCP config currently points `GIT_PYTHON_GIT_EXECUTABLE` at `D:\Program Files\Git\cmd\git.exe`; verify that path exists on the machine before relying on Git MCP.

## Use in Claude Code

1. Restart Claude Code in this project.
2. Run `/mcp` and approve the project MCP servers if prompted.
3. Ask Claude to inspect the repository or review recent changes with Git context.

Example prompts:

```text
使用 git MCP 检查当前仓库改动，并按 bug、安全、性能、可维护性四类做代码审查。
```

```text
使用 git MCP 查看最近一次提交的 diff，然后给出高风险问题和需要补充的测试。
```

## Optional MCP servers

These servers are useful for code review, but they need API keys, local services, or extra setup. Do not add them to the active config until the required credentials are available.

### claude-context

Purpose: semantic code search over large repositories.

Typical Claude Code command:

```powershell
claude mcp add-json claude-context '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@zilliz/claude-context-mcp@latest"]
}'
```

Before enabling, set the embedding and vector database environment variables required by your chosen provider, such as `OPENAI_API_KEY`, Zilliz Cloud connection values, or local Milvus settings.

### GitHub MCP

Purpose: work with GitHub repositories, issues, pull requests, comments, and review workflows.

Claude Code remote server example:

```powershell
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
```

Set `GITHUB_PERSONAL_ACCESS_TOKEN` before enabling this. Use a token with only the repository scopes you need.

### CodeGraphContext

Purpose: build a code knowledge graph for cross-file and architecture review.

Typical setup:

```powershell
pip install codegraphcontext
cgc init
cgc index
cgc mcp start
```

The project currently does not have `cgc` installed. Configure this only after choosing the database/index storage location.

### code-reviewer-mcp

Purpose: structured automated review with model-backed findings, usually via OpenRouter or Claude-compatible providers.

This server generally needs a local clone/build and model provider keys such as `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`. Keep it out of active MCP config until the provider key is set, otherwise Claude/Cursor may start with a failing MCP server.

## Local checks

Validate JSON config:

```powershell
python -m json.tool .mcp.json
python -m json.tool .cursor/mcp.json
python -m json.tool .vscode/mcp.json
```

Confirm Git MCP command is available:

```powershell
uvx mcp-server-git --help
```

Confirm the required local commands are visible:

```powershell
where.exe claude
where.exe git
where.exe bash
claude mcp list
```
