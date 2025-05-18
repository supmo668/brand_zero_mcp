#!/usr/bin/env python
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\tests\test_mcp_server.py

import asyncio
import json
import logging
import os
import sys
import argparse
import aiohttp
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_mcp_api(brand_name: str, base_url: str = "http://localhost:8080"):
    """
    Test the MCP API by sending a research request
    """
    logger.info(f"Testing MCP API at {base_url} for brand: {brand_name}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the describe endpoint
            logger.info("Testing MCP describe endpoint...")
            describe_url = f"{base_url}/mcp/describe"
            async with session.get(describe_url) as response:
                if response.status != 200:
                    logger.error(f"Error from describe endpoint: {response.status}")
                    return
                
                describe_data = await response.json()
                logger.info("MCP description:")
                pprint(describe_data)
            
            # Test the execute endpoint
            logger.info("Testing MCP execute endpoint...")
            execute_url = f"{base_url}/mcp/execute"
            mcp_request = {
                "inputs": {
                    "brand_name": brand_name
                }
            }
            
            logger.info(f"Sending request: {mcp_request}")
            
            async with session.post(execute_url, json=mcp_request) as response:
                if response.status != 200:
                    logger.error(f"Error from execute endpoint: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Response: {error_text}")
                    return
                
                result = await response.json()
                
                # Save the result to a file
                output_dir = os.path.join(os.path.dirname(__file__), 'output')
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_mcp_result.json")
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                logger.info(f"MCP results saved to {output_file}")
                
                # Extract and print some key information
                if "outputs" in result and "result" in result["outputs"]:
                    try:
                        analysis_result = json.loads(result["outputs"]["result"])
                        print("\n" + "="*50)
                        print(f"MCP ANALYSIS RESULTS: {brand_name}")
                        print("="*50)
                        print(f"Visibility Score: {analysis_result.get('visibility_score', 'N/A')}")
                        print(f"Simulated Queries: {len(analysis_result.get('simulated_queries', []))}")
                        print(f"Marketing Insights: {len(analysis_result.get('insights', []))}")
                        print(f"\nResults saved to: {output_file}")
                    except Exception as e:
                        logger.error(f"Error parsing result: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error testing MCP API: {str(e)}")

def main():
    """
    Main entry point for the test script
    """
    parser = argparse.ArgumentParser(description="Test the BrandZero MCP API")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--url", help="Base URL for the MCP API", default="http://localhost:8080")
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(test_mcp_api(args.brand, args.url))

if __name__ == "__main__":
    main()
