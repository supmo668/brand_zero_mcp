"""
Brand Zero MCP server for brand presence research.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import logging
import json
from typing import List, Optional, Dict, Any
import asyncio
from pydantic import BaseModel, Field

from fastmcp import FastMCP

from pipeline import run_analysis_pipeline
from models import TransformationState, BrandAnalysisResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brand_zero.server")

# Initialize FastMCP server
app = FastMCP("Brand Zero Presence Analyzer")

@app.tool()
async def analyze_brand_presence(brand_or_product: str) -> Dict[str, Any]:
    """
    Analyze the online presence of a brand or product.
    
    This tool simulates search queries about the brand or product, performs multiple searches,
    and analyzes the results to determine brand presence and visibility.
    
    Args:
        brand_or_product: The name of the brand or product to analyze
    
    Returns:
        Analysis of the brand's online presence with recommendations
    """
    logger.info(f"Received brand presence analysis request for: {brand_or_product}")
    
    # Run the analysis pipeline
    state: TransformationState = await run_analysis_pipeline(brand_or_product)
    
    # Prepare simulated queries list for the response
    simulated_queries = [q.query for q in state.simulated_queries]
    
    # Check if there was an error
    if state.error:
        return TransformationState(**{
            "status": "error",
            "brand_or_product": brand_or_product,
            "simulated_queries": simulated_queries,
            "analysis_summary": None,
            "error": state.error
        })
    
    # Prepare analysis summary
    analysis_summary = state.analysis_result.summary if state.analysis_result else "No analysis available"
    
    # Get presence score
    presence_score = state.analysis_result.presence_score if state.analysis_result else 0
    
    # Return final response
    return BrandAnalysisResult(**state.analysis_summary.dict())

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
        logger.info(f"Starting Brand Zero MCP server on port {args.port}")
        app.run(transport="sse", host="127.0.0.1", port=args.port)
    elif args.brand:
        # CLI mode
        result = asyncio.run(analyze_brand_presence(args.brand))
        print(json.dumps(result, indent=2))
        
        # Save result to file
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Result saved to result.json")
    else:
        parser.print_help()
