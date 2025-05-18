# BrandZero Test Suite

This directory contains tests for the BrandZero project.

## Available Tests

1. `test_pipeline.py` - Tests the complete brand research pipeline
2. `test_langgraph.py` - Tests the LangGraph workflow execution
3. `test_mcp_server.py` - Tests the MCP server API endpoints
4. `test_agent.py` - Tests the uAgent implementation
5. `run_quick_test.py` - Simplified test for quick validation
6. `test_mcp.py` - Direct test of the MCP protocol

## Running Tests

### Prerequisites

- Make sure you have all dependencies installed
- Ensure `.env` file is properly configured with API keys

### Running Individual Tests

To run the pipeline test:
```bash
python test_pipeline.py "Your Brand Name"
```

To run the LangGraph test:
```bash
python test_langgraph.py "Your Brand Name" --debug
```

To run the MCP server test (server must be running):
```bash
python test_mcp_server.py "Your Brand Name"
```

To run the agent test (agent must be running):
```bash
python test_agent.py "Your Brand Name" --address agent_address
```

### Running All Tests

To run all tests in sequence:
```bash
bash run_all_tests.sh "Your Brand Name"
```

## Output

Test results are saved in the `output` directory with the following formats:
- `{brand_name}_langgraph_result.json` - Raw LangGraph output
- `{brand_name}_analysis.json` - Full brand analysis result
- `{brand_name}_summary.md` - Markdown summary of the analysis
- `{brand_name}_mcp_result.json` - MCP API response
- `{brand_name}_agent_result.json` - uAgent response
