#!/usr/bin/env python
"""
Test script for the BrandZero MCP functionality
This demonstrates how to connect to and use the MCP server directly
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
import argparse
from pprint import pprint
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_mcp(brand_name: str, host: str = "localhost", port: int = 8080):
    """Test the MCP server by sending a brand analysis request"""
    url = f"http://{host}:{port}/mcp/execute"
    
    request_data = {
        "inputs": {
            "brand_name": brand_name
        }
    }
    
    logger.info(f"Sending MCP request to {url}")
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request_data) as response:
                if response.status != 200:
                    logger.error(f"Error: HTTP {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return
                
                result = await response.json()
                
                # Save the raw result
                output_dir = os.path.join(os.path.dirname(__file__), 'output')
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_mcp_result.json")
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                logger.info(f"MCP response saved to {output_file}")
                
                # Process and display results
                if "outputs" in result and "result" in result["outputs"]:
                    try:
                        analysis = json.loads(result["outputs"]["result"])
                        
                        print("\n" + "="*50)
                        print(f"MCP ANALYSIS RESULTS: {brand_name}")
                        print("="*50)
                        
                        if "visibility_score" in analysis:
                            print(f"Visibility Score: {analysis['visibility_score']}/100")
                        
                        if "simulated_queries" in analysis:
                            queries = analysis["simulated_queries"]
                            print(f"\nSimulated Queries: {len(queries)}")
                            for i, q in enumerate(queries[:3], 1):
                                print(f"  {i}. {q['text']}")
                            if len(queries) > 3:
                                print(f"  ... and {len(queries) - 3} more")
                        
                        if "insights" in analysis:
                            insights = analysis["insights"]
                            print(f"\nKey Marketing Insights: {len(insights)}")
                            for i, insight in enumerate(insights[:3], 1):
                                print(f"  {i}. {insight['category']}: {insight['description'][:100]}...")
                            if len(insights) > 3:
                                print(f"  ... and {len(insights) - 3} more")
                        
                        print(f"\nDetailed results saved to: {output_file}")
                        
                    except Exception as e:
                        logger.error(f"Error processing response: {str(e)}")
                else:
                    logger.warning("Unexpected response format")
                    pprint(result)
    
    except aiohttp.ClientError as e:
        logger.error(f"Connection error: {str(e)}")
        print("\nERROR: Could not connect to the MCP server.")
        print("Make sure the server is running with: python -m brand_zero_mcp.server")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the BrandZero MCP")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--host", help="MCP server host", default="localhost")
    parser.add_argument("--port", help="MCP server port", type=int, default=8080)
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Run the test
    asyncio.run(test_mcp(args.brand, args.host, args.port))
