"""
Analysis pipeline for the Brand Zero MCP application.
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from langchain_core.output_parsers import PydanticOutputParser

import logging
logger = logging.getLogger("brand_zero.pipeline")

from models import (
    TransformationState, 
    SimulatedQuery,
    SearchResult,
    BrandAnalysisResult,
    StepStatus
)
from llm_service import create_analysis_step
from llm_providers import OpenAISearchProvider, PerplexitySearchProvider
from utils import CONFIG, extract_json_from_text, format_sources_for_prompt

class QueryListParser(BaseModel):
    """Parser for query list."""
    queries: List[str] = Field(description="List of generated search queries")

async def simulate_queries(brand_or_product: str, state: TransformationState) -> List[SimulatedQuery]:
    """
    Simulate search queries that might lead to the brand/product.
    
    Args:
        brand_or_product: The brand or product name
        state: The state object
    
    Returns:
        List of simulated queries
    """
    logger.info(f"Simulating queries for {brand_or_product}")
    
    # Create parser
    parser = PydanticOutputParser(pydantic_object=QueryListParser)
    
    # Get simulate queries count from config
    simulate_queries_count = CONFIG["pipeline"].get("SIMULATE_QUERIES_COUNT", 10)
    
    # Call LLM to generate queries
    result = await create_analysis_step(
        state=state,
        step_name="query_generation",
        prompt_key="QUERY_GENERATOR",
        input_variables={
            "brand_or_product": brand_or_product,
            "simulate_queries_count": simulate_queries_count
        },
        parser=parser
    )
    
    if not result:
        logger.error("Failed to generate queries")
        return []
    
    # Convert to SimulatedQuery objects
    queries = []
    for query_text in result.queries:
        queries.append(SimulatedQuery(query=query_text))
    
    return queries

async def search_queries(
    simulated_queries: List[SimulatedQuery], 
    state: TransformationState
) -> List[SearchResult]:
    """
    Search for the simulated queries using multiple search providers.
    
    Args:
        simulated_queries: List of simulated queries
        state: The state object
    
    Returns:
        List of search results
    """
    logger.info(f"Searching for {len(simulated_queries)} queries")
    
    # Initialize search providers
    search_providers = [
        OpenAISearchProvider(),
        PerplexitySearchProvider()
    ]
    
    # Get batch size from config
    batch_size = CONFIG["pipeline"].get("BATCH_SIZE", 5)
    
    all_results = []
    for i in range(0, len(simulated_queries), batch_size):
        batch = simulated_queries[i:i+batch_size]
        batch_tasks = []
        
        # Create tasks for each query and provider
        for query in batch:
            for provider in search_providers:
                batch_tasks.append(provider.search(query.query))
        
        # Execute batch
        logger.info(f"Executing batch of {len(batch_tasks)} search tasks")
        batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Process responses
        result_idx = 0
        for query in batch:
            for provider in search_providers:
                response = batch_responses[result_idx]
                result_idx += 1
                
                if isinstance(response, Exception):
                    logger.error(f"Error searching {query.query} with {provider.name}: {response}")
                    continue
                
                search_result = SearchResult(
                    query=query.query,
                    provider=response["provider"],
                    content=response["content"],
                    sources=response["sources"]
                )
                all_results.append(search_result)
    
    return all_results

async def analyze_results(
    brand_or_product: str, 
    search_results: List[SearchResult], 
    state: TransformationState
) -> Optional[BrandAnalysisResult]:
    """
    Analyze search results to check brand presence.
    
    Args:
        brand_or_product: The brand or product name
        search_results: List of search results
        state: The state object
    
    Returns:
        Analysis result or None if error
    """
    logger.info(f"Analyzing results for {brand_or_product}")
    
    # Prepare sources for analysis
    all_sources = []
    max_sources_per_query = CONFIG["pipeline"].get("MAX_SOURCES_PER_QUERY", 5)
    
    for result in search_results:
        # Limit sources per query to avoid prompt size issues
        sources = result.sources[:max_sources_per_query]
        all_sources.extend(sources)
    
    # Format sources for prompt
    formatted_sources = format_sources_for_prompt(all_sources)
    
    # Call LLM to analyze sources
    result = await create_analysis_step(
        state=state,
        step_name="judge_analysis",
        prompt_key="JUDGE_ANALYZER",
        input_variables={
            "brand_or_product": brand_or_product,
            "sources": formatted_sources
        },
        parser=None  # No parser for now, we'll get raw markdown
    )
    
    if not result:
        logger.error("Failed to analyze results")
        return None
    
    # Create analysis result
    # Note: The actual fields would need to be extracted from the markdown
    # For now, we'll create a placeholder with the raw result
    analysis_result = BrandAnalysisResult(
        brand_name=brand_or_product,
        frequency=0,  # This would need to be extracted from the response
        summary=result,
        competitors=[],
        sentiment="",
        recommendations=[]
    )
    
    return analysis_result

async def run_analysis_pipeline(brand_or_product: str) -> TransformationState:
    """
    Run the complete analysis pipeline.
    
    Args:
        brand_or_product: The brand or product name
    
    Returns:
        Completed state object
    """
    logger.info(f"Starting analysis pipeline for {brand_or_product}")
    
    # Initialize state
    state = TransformationState(brand_or_product=brand_or_product)
    
    try:
        # Step 1: Simulate queries
        queries = await simulate_queries(brand_or_product, state)
        if not queries:
            state.error = "Failed to simulate queries"
            return state
        
        state.simulated_queries = queries
        logger.info(f"Generated {len(queries)} simulated queries")
        
        # Step 2: Search queries
        search_results = await search_queries(queries, state)
        if not search_results:
            state.error = "Failed to search queries"
            return state
            
        state.search_results = search_results
        logger.info(f"Completed {len(search_results)} searches")
        
        # Step 3: Analyze results
        analysis_result = await analyze_results(brand_or_product, search_results, state)
        if not analysis_result:
            state.error = "Failed to analyze results"
            return state
            
        state.analysis_result = analysis_result
        logger.info("Completed analysis")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in analysis pipeline: {str(e)}")
        state.error = f"Pipeline error: {str(e)}"
        return state
