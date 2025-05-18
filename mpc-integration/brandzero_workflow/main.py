"""
Brand Zero MCP server for brand presence research.
"""
from dotenv import load_dotenv
load_dotenv()

import logging
import json
import asyncio

from fastmcp import FastMCP

from pipeline import run_analysis_pipeline, ensure_brand_analysis_result
from models import TransformationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brand_zero.server")

# Initialize FastMCP server
app = FastMCP("Brand Zero Presence Analyzer")

@app.tool()
async def analyze_brand_presence(brand_or_product: str) -> dict:
    """
    Analyze the online presence of a brand or product.
    
    This tool simulates search queries about the brand or product, performs multiple searches,
    and analyzes the results to determine brand presence and visibility.
    
    Args:
        brand_or_product: The name of the brand or product to analyze
    
    Returns:
        Analysis of the brand's online presence with recommendations
    """
    logger.info("Received brand presence analysis request for: %s", brand_or_product)
    
    # Run the analysis pipeline
    state = await run_analysis_pipeline(brand_or_product)
    
    # Prepare simulated queries list for the response
    simulated_queries = [q.query for q in state.simulated_queries]
    
    # Check if there was an error
    if state.error:
        return TransformationState(
            status="error",
            brand_or_product=brand_or_product,
            simulated_queries=simulated_queries,
            analysis_summary=None,
            error=state.error
        ).model_dump()
    
    # Return final response
    return ensure_brand_analysis_result(state.analysis_result).model_dump()

# CLI test runner for local dev/demo
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brand Zero MCP CLI")
    parser.add_argument("--serve", action="store_true", help="Start MCP HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--brand", type=str, help="Brand or product name to analyze (CLI mode)")
    
    args = parser.parse_args()
    
    if args.serve:
        # Start the FastMCP server using the correct syntax
        logger.info("Starting Brand Zero MCP server on port %d", args.port)
        app.run(transport="sse", host="127.0.0.1", port=args.port)
    elif args.brand:
        # CLI mode
        result = asyncio.run(analyze_brand_presence(args.brand))
        print(json.dumps(result, indent=2))
        
        # Save result to file
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to result.json")
    else:
        parser.print_help()
