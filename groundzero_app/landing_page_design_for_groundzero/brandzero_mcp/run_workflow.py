#!/usr/bin/env python
"""
Command-line tool to run brand presence analysis workflow.
This script allows you to directly run the brand presence analysis
without starting the MCP server.
"""
import os
import asyncio
import argparse
import logging
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brand_zero.workflow")

# Import local modules
from .pipeline import run_analysis_pipeline, ensure_brand_analysis_result
from .models import TransformationState, BrandAnalysisResult

def format_simulated_queries(state: TransformationState) -> str:
    """Format simulated queries for display."""
    if not state.simulated_queries:
        return "No queries generated"
    
    result = "Simulated Queries:\n"
    for i, query in enumerate(state.simulated_queries, 1):
        result += f"{i}. {query.query}\n"
    return result

def format_search_results(state: TransformationState) -> str:
    """Format search results summary for display."""
    if not state.search_results:
        return "No search results available"
    
    providers = set()
    query_count = set()
    source_count = 0
    
    for result in state.search_results:
        providers.add(result.provider)
        query_count.add(result.query)
        source_count += len(result.sources)
    
    return (f"Search Results Summary:\n"
            f"- Total Queries: {len(query_count)}\n"
            f"- Search Providers: {', '.join(providers)}\n"
            f"- Total Sources: {source_count}\n")

async def run_workflow(brand_or_product: str, output_file: str = None, verbose: bool = False) -> Optional[BrandAnalysisResult]:
    """
    Run the brand presence analysis workflow and return a BrandAnalysisResult.
    """
    try:
        logger.info("Starting brand presence analysis for '%s'", brand_or_product)
        state = await run_analysis_pipeline(brand_or_product)

        # If state is a dict (LangGraph), convert to TransformationState
        if isinstance(state, dict):
            state = TransformationState(**state)

        # Print simulated queries if verbose
        if verbose:
            print("\n" + format_simulated_queries(state))
            print("\n" + format_search_results(state))

        # Print analysis results
        analysis_result = None
        if state.analysis_result:
            analysis_result = ensure_brand_analysis_result(state.analysis_result)
            print("\nAnalysis Results:")
            print("=" * 50)
            print(analysis_result.summary)
            print("=" * 50)
        else:
            logger.warning("No analysis results available")
            return None

        # Save results to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis_result.model_dump_json(indent=2, ensure_ascii=False))
            logger.info("Results saved to %s", output_file)
        return analysis_result
    except Exception as e:
        logger.error("Error running workflow: %s", e)
        raise

def main():
    """Main entry point."""
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "PERPLEXITY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in a .env file or in your environment")
        return

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run brand presence analysis workflow")
    parser.add_argument("brand", type=str, help="Brand or product name to analyze")
    parser.add_argument("-o", "--output", type=str, default="result.json", help="Output file for results (JSON format)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    # Run the workflow
    asyncio.run(run_workflow(args.brand, args.output, args.verbose))

if __name__ == "__main__":
    main()
