#!/bin/bash
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\run_tests.sh

# Set the brand name to test
BRAND_NAME=${1:-"Tesla"}

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Create the output directory
mkdir -p tests/output

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}Running BrandZero Tests${NC}"
echo -e "${YELLOW}Brand: ${BRAND_NAME}${NC}"
echo -e "${YELLOW}=====================================${NC}"

# Run the pipeline test
echo -e "\n${GREEN}Running Pipeline Test...${NC}"
python tests/test_pipeline.py "${BRAND_NAME}"

# Run the LangGraph test
echo -e "\n${GREEN}Running LangGraph Test...${NC}"
python tests/test_langgraph.py "${BRAND_NAME}" --debug

# Run the MCP server test (only if server is running)
echo -e "\n${YELLOW}Do you want to run the MCP server test? (y/n)${NC}"
read -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "\n${GREEN}Starting MCP server in the background...${NC}"
  python -m brand_zero_mcp.server &
  SERVER_PID=$!
  
  # Wait for server to start
  echo "Waiting 5 seconds for server to start..."
  sleep 5
  
  echo -e "\n${GREEN}Running MCP Server Test...${NC}"
  python tests/test_mcp_server.py "${BRAND_NAME}"
  
  # Kill the server process
  kill $SERVER_PID
else
  echo -e "\n${YELLOW}Skipping MCP Server Test${NC}"
fi

echo -e "\n${GREEN}All tests completed${NC}"
echo -e "${GREEN}Results saved in tests/output directory${NC}"
