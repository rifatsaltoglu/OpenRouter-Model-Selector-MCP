# OpenRouter Model Selector MCP

OpenRouter Model Selector is a Model Context Protocol (MCP) server that helps AI assistants automatically find, filter, and rank the best AI models for a specific task using the OpenRouter API.

Whether you need a model for coding, image generation, text-to-speech (TTS), or transcription (STT), this tool queries the live OpenRouter directory, groups them by your requested modality, and ranks the top 10 models based on:
1. **Price** (1 to 5 stars - 5 stars being the most expensive).
2. **Benchmark / Performance** (1 to 5 stars based on intelligence index or Elo rating).

## Features
- **Zero Configuration:** No API keys required. It uses OpenRouter's public `/api/v1/models` endpoint.
- **Smart Modality Routing:** Understands keywords to correctly filter for `image-understanding`, `video-understanding`, `transcription`, `speech`, `image-generation`, and `video-generation`.
- **Dynamic Pricing Calculation:** Accurately compares prompt/completion/image output prices to give a relative cost score.
- **FastMCP Built:** Built on top of `fastmcp` for quick integration with MCP-compatible clients like Claude Desktop, Cursor, or Google Antigravity.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/openrouter-model-selector-mcp.git
cd openrouter-model-selector-mcp
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage & Configuration

To use this with any MCP-compatible AI assistant, you need to add it to your MCP configuration file (e.g., `mcp.json` or `claude_desktop_config.json`).

Here is an example configuration:

```json
{
  "mcpServers": {
    "openrouter-model-selector": {
      "command": "/absolute/path/to/your/cloned/repo/.venv/bin/python",
      "args": [
        "/absolute/path/to/your/cloned/repo/openrouter_agent_selector.py"
      ]
    }
  }
}
```

*Make sure to replace `/absolute/path/to/your/cloned/repo/` with the actual path on your machine.*

## How it works

When connected, your AI assistant will have access to a tool called `select_best_agent`. 
If you ask your AI: *"Find me an AI model for text to speech"*, it will call this tool with `topic="text to speech"`, fetch the relevant models, and present you with a Markdown-formatted list containing the stars for Price and Benchmark.

## Security & Privacy
This tool does not require or transmit any private API keys. It only reads public model catalog data from OpenRouter.

## License
MIT License

## Security Maintainer
- **Lead Security Maintainer:** Rifat Saltoğlu ([@rifatsaltoglu](https://github.com/rifatsaltoglu) / `rifatsaltoglu@gmail.com`)
- See [SECURITY.md](./SECURITY.md) for our coordinated vulnerability disclosure policy and published security advisories (`OR-MCP-2026-001`).
