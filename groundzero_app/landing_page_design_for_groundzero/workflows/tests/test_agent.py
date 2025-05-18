#!/usr/bin/env python
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\tests\test_agent.py

import asyncio
import json
import logging
import os
import sys
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a test agent to communicate with the BrandZero agent
test_agent = Agent(
    name="test_agent",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
    seed="test_agent_seed"
)

# Fund the agent if needed
fund_agent_if_low(test_agent.wallet.address())

# Create a protocol for handling responses
test_protocol = Protocol("test_protocol")

@test_protocol.on_message
async def handle_response(ctx: Context, sender: str, msg: dict):
    """Handle responses from the BrandZero agent"""
    if "error" in msg:
        logger.error(f"Error received: {msg['error']}")
    elif "status" in msg and msg["status"] == "success":
        logger.info("Received successful response!")
        
        # Parse and save the result
        try:
            result = json.loads(msg["result"])
            
            # Save to file
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            brand_name = result.get("brand_name", "unknown_brand")
            output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_agent_result.json")
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Results saved to {output_file}")
            
            # Print summary
            print("\n" + "="*50)
            print(f"AGENT ANALYSIS RESULTS: {brand_name}")
            print("="*50)
            print(f"Visibility Score: {result.get('visibility_score', 'N/A')}")
            print(f"Simulated Queries: {len(result.get('simulated_queries', []))}")
            print(f"Marketing Insights: {len(result.get('insights', []))}")
            
            # Signal to stop the agent
            ctx.storage.set("received_response", True)
            
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}")
    else:
        logger.warning(f"Unexpected message format: {msg}")

# Register the protocol
test_agent.include(test_protocol)

async def send_request(brand_name: str, target_address: str):
    """Send a brand research request to the BrandZero agent"""
    # Wait for the agent to start up
    await asyncio.sleep(2)
    
    @test_agent.on_interval(period=60.0, messages_limit=1)
    async def request_research(ctx: Context):
        brand_name = ctx.storage.get("brand_name")
        target = ctx.storage.get("target_address")
        
        logger.info(f"Sending research request for brand: {brand_name} to {target}")
        
        await ctx.send(target, {
            "brand_name": brand_name
        })

    # Store values for the interval task
    test_agent.storage.set("brand_name", brand_name)
    test_agent.storage.set("target_address", target_address)
    
    # Run the agent
    test_agent.run()

def main():
    """
    Main entry point for the test script
    """
    parser = argparse.ArgumentParser(description="Test the BrandZero uAgent")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--address", help="Address of the BrandZero agent", required=True)
    args = parser.parse_args()
    
    # Check environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY environment variable is not set in this process. Make sure it's set for the agent process.")
    
    if not os.environ.get("PERPLEXITY_API_KEY"):
        logger.warning("PERPLEXITY_API_KEY environment variable is not set in this process. Make sure it's set for the agent process.")
    
    # Send the request
    asyncio.run(send_request(args.brand, args.address))

if __name__ == "__main__":
    main()
