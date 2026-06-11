import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('backend/app/services/ai_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove top-level ClaudeProvider import
content = content.replace(
    "from ..ai_providers.claude_provider import ClaudeProvider\n",
    ""
)

# 2. Move ClaudeProvider import inside get_provider function
old_get_provider = '''    if provider_name == "claude":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("AI服务未配置 ANTHROPIC_API_KEY，请先在环境变量或 .env 中设置后再使用。")
        return ClaudeProvider()'''

new_get_provider = '''    if provider_name == "claude":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("AI服务未配置 ANTHROPIC_API_KEY，请先在环境变量或 .env 中设置后再使用。")
        from ..ai_providers.claude_provider import ClaudeProvider
        return ClaudeProvider()'''

content = content.replace(old_get_provider, new_get_provider)

with open('backend/app/services/ai_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed: ClaudeProvider import is now lazy')
