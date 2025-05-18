# BrandZero - Brand Presence Research MCP

BrandZero is a Model Context Protocol (MCP) server that analyzes brand presence and consumer search behavior using multiple LLM platforms. It helps marketers understand how their brands are discovered and perceived online.

## Features

- Simulates natural consumer queries that could lead to brand discovery
- Multi-LLM research using OpenAI's Deep Research and Perplexity's Sonar
- Source analysis and brand mention tracking
- Competitive intelligence gathering
- Marketing insights generation
- Brand visibility scoring
- Comprehensive markdown reports with linked sources

## Prerequisites

- Python 3.9+
- OpenAI API key
- Perplexity API key
- FetchAI's uAgent framework

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```

## Usage

### 1. Environment Setup

First, set up your environment variables:

```bash
cp .env.template .env
```

Edit the `.env` file and add your API keys:
- `OPENAI_API_KEY`: Your OpenAI API key with access to GPT-4
- `PERPLEXITY_API_KEY`: Your Perplexity API key for Sonar-pro access

### 2. Quick Start: Run the Pipeline Directly

To quickly run the brand analysis pipeline directly:

```bash
python run_pipeline.py "Your Brand Name"
```

This will execute the complete pipeline and generate a report.

### 3. Using the MCP Server

Start the MCP server:

```bash
python -m brand_zero_mcp.server
```

Send API requests to:
- MCP Describe: `GET http://localhost:8080/mcp/describe`
- MCP Execute: `POST http://localhost:8080/mcp/execute` with JSON body:
  ```json
  {
    "inputs": {
      "brand_name": "your_brand_name"
    }
  }
  ```

### 4. Using the uAgent

Start the agent:

```bash
python agent.py
```

Send a research request to the agent:

```python
from uagents import Agent, Context

async def request_research(ctx: Context):
    await ctx.send("agent_address", {
        "brand_name": "your_brand_name"
    })
```

### 5. Running Tests

For quick testing:

```bash
cd tests
python run_quick_test.py "Your Brand Name"
```

For comprehensive pipeline testing:

```bash
python tests/test_pipeline.py "Your Brand Name"
```

For full test suite:

```bash
bash tests/run_all_tests.sh "Your Brand Name"
```

## Architecture

- `models.py` - Pydantic data models
- `llm_wrappers.py` - LLM API integration wrappers
- `pipeline.py` - LangGraph-based research pipeline
- `agent.py` - uAgent MCP server implementation

## Development

To run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
