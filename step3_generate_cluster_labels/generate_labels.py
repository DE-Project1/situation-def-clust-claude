from claude_api_wrapper import ClaudeAPIWrapper

async def generate_cluster_label(definition_list):
    claude = ClaudeAPIWrapper()
    label = await claude.generate_cluster_label_async(definition_list)
    return label