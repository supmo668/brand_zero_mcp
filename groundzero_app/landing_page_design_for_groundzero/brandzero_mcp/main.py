"""
Brand Zero MCP server for brand presence research.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import logging
from typing import List, Optional, Dict, Any
import asyncio
from pydantic import BaseModel, Field

from fastmcp import FastMCP

from pipeline import run_analysis_pipeline
from models import TransformationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brand_zero.server")

# Initialize FastMCP server
app = FastMCP("Brand Zero Presence Analyzer")

# Define request and response models
class BrandZeroRequest(BaseModel):
    brand_or_product: str = Field(..., description="The brand or product name to research")

class BrandZeroResponse(BaseModel):
    status: str
    brand_or_product: str
    simulated_queries: List[str] = Field(default_factory=list)
    analysis_summary: Optional[str] = None
    error: Optional[str] = None

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
    state = await run_analysis_pipeline(brand_or_product)
    
    # Prepare simulated queries list for the response
    simulated_queries = [q.query for q in state.simulated_queries]
    
    # Check if there was an error
    if state.error:
        return {
            "status": "error",
            "brand_or_product": brand_or_product,
            "simulated_queries": simulated_queries,
            "analysis_summary": None,
            "error": state.error
        }
    
    # Prepare analysis summary
    analysis_summary = state.analysis_result.summary if state.analysis_result else "No analysis available"
    
    # Return final response
    return {
        "status": "success",
        "brand_or_product": brand_or_product,
        "simulated_queries": simulated_queries,
        "analysis_summary": analysis_summary,
        "error": None
    }

# Optional: CLI test runner for local dev/demo
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brand Zero MCP CLI")
    parser.add_argument("brand", type=str, help="Brand or product name to analyze")
    args = parser.parse_args()
    result = asyncio.run(analyze_brand_presence(args.brand))
    print(result)
