"""
Brand Zero MCP server for brand presence research.
"""
import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from mcp import App, Response, Request, Registry, ChunkData
from mcp.extensions import ExtensionBuilder, ChunkDataKind

# Import local modules
from pipeline import run_analysis_pipeline
from models import TransformationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brand_zero.server")

# Initialize Model Context Protocol (MCP) app
app = App("Brand Zero Presence Analyzer")
ext = ExtensionBuilder(app.registry)

# Define request and response models
class BrandZeroRequest(BaseModel):
    brand_or_product: str = Field(..., description="The brand or product name to research")

class BrandZeroResponse(BaseModel):
    status: str
    brand_or_product: str
    simulated_queries: List[str] = Field(default_factory=list)
    analysis_summary: Optional[str] = None
    error: Optional[str] = None

@ext.tool("analyze_brand_presence")
async def analyze_brand_presence(
    request: Request,
    brand_or_product: str = Body(..., description="Brand or product name to analyze")
) -> Response:
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
    
    try:
        # Start streaming response
        await request.stream.send(ChunkData(
            kind=ChunkDataKind.TEXT,
            data=f"Starting analysis for '{brand_or_product}'..."
        ))
        
        # Run the analysis pipeline
        state = await run_analysis_pipeline(brand_or_product)
        
        # Prepare simulated queries list for the response
        simulated_queries = [query.query for query in state.simulated_queries]
        
        # Stream progress updates
        await request.stream.send(ChunkData(
            kind=ChunkDataKind.TEXT,
            data=f"Generated {len(simulated_queries)} search queries"
        ))
        
        # Stream search results progress
        await request.stream.send(ChunkData(
            kind=ChunkDataKind.TEXT,
            data=f"Completed {len(state.search_results)} searches"
        ))
        
        # Check if there was an error
        if state.error:
            await request.stream.send(ChunkData(
                kind=ChunkDataKind.TEXT,
                data=f"Error: {state.error}"
            ))
            
            return Response(
                status="error",
                error=state.error,
                brand_or_product=brand_or_product,
                simulated_queries=simulated_queries
            )
        
        # Stream analysis result
        analysis_summary = state.analysis_result.summary if state.analysis_result else "No analysis available"
        await request.stream.send(ChunkData(
            kind=ChunkDataKind.TEXT,
            data=f"Analysis complete!"
        ))
        
        # Send the full analysis text as markdown
        await request.stream.send(ChunkData(
            kind=ChunkDataKind.MARKDOWN,
            data=analysis_summary
        ))
        
        # Return final response
        return Response(
            status="success",
            brand_or_product=brand_or_product,
            simulated_queries=simulated_queries,
            analysis_summary=analysis_summary
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_brand_presence: {str(e)}")
        return Response(
            status="error",
            error=str(e),
            brand_or_product=brand_or_product
        )

if __name__ == "__main__":
    # Start the MCP server
    port = int(os.environ.get("PORT", 8000))
    app.start(port=port)
    logger.info(f"Brand Zero MCP server running on port {port}")
