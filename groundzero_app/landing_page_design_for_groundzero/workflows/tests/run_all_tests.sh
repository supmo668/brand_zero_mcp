#!/bin/bash
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\tests\run_all_tests.sh

# Check if a brand name was provided
if [ -z "$1" ]; then
  echo "Error: Brand name is required."
  echo "Usage: $0 <brand_name>"
  exit 1
fi

BRAND_NAME="$1"

# Create output directory
mkdir -p "$(dirname "$0")/output"

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}Running All BrandZero Tests${NC}"
echo -e "${YELLOW}Brand: ${BRAND_NAME}${NC}"
echo -e "${YELLOW}=====================================${NC}"

# Function to run a test
run_test() {
  TEST_NAME="$1"
  shift
  echo -e "\n${YELLOW}Running ${TEST_NAME}...${NC}"
  
  # Run the test and capture exit code
  python "$@"
  EXIT_CODE=$?
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ ${TEST_NAME} completed successfully${NC}"
  else
    echo -e "${RED}✗ ${TEST_NAME} failed with exit code ${EXIT_CODE}${NC}"
  fi
  
  # Add a separator
  echo -e "${YELLOW}-------------------------------------${NC}"
}

# Run all tests
DIR="$(dirname "$0")"

# 1. Test the LangGraph pipeline
run_test "LangGraph Pipeline Test" "${DIR}/test_langgraph.py" "${BRAND_NAME}"

# 2. Test the full pipeline
run_test "Full Pipeline Test" "${DIR}/test_pipeline.py" "${BRAND_NAME}"

# 3. Test the MCP server (make sure the server is running first)
echo -e "\n${YELLOW}NOTE: The following test requires the MCP server to be running.${NC}"
echo -e "${YELLOW}If the server is not running, this test will fail.${NC}"
read -p "Is the MCP server running? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  run_test "MCP Server Test" "${DIR}/test_mcp_server.py" "${BRAND_NAME}"
else
  echo -e "${YELLOW}Skipping MCP Server Test${NC}"
fi

# 4. Test the uAgent (make sure the agent is running first)
echo -e "\n${YELLOW}NOTE: The following test requires the uAgent to be running.${NC}"
echo -e "${YELLOW}If the agent is not running, this test will fail.${NC}"
read -p "Is the uAgent running? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  read -p "Enter the agent address: " AGENT_ADDRESS
  run_test "uAgent Test" "${DIR}/test_agent.py" "${BRAND_NAME}" "--address" "${AGENT_ADDRESS}"
else
  echo -e "${YELLOW}Skipping uAgent Test${NC}"
fi

echo -e "\n${GREEN}All tests completed!${NC}"
echo -e "${YELLOW}Results can be found in: ${DIR}/output${NC}"
