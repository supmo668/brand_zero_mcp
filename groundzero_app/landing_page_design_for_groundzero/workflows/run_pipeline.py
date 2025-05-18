#!/usr/bin/env python
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\run_pipeline.py

import asyncio
import argparse
import logging
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pipeline import BrandResearchPipeline
from models import BrandAnalysisResult

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_pipeline(brand_name: str, output_file: str = None):
    """
    Run the brand research pipeline directly
    """
    logger.info(f"Starting brand research for: {brand_name}")
    
    pipeline = BrandResearchPipeline()
    result = await pipeline.run_analysis(brand_name)
    
    # Save result to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result.dict(), f, indent=2)
        logger.info(f"Results saved to {output_file}")
    
    # Print summary
    print("\n===== BRAND ANALYSIS SUMMARY =====")
    print(f"Brand: {brand_name}")
    print(f"Visibility Score: {result.visibility_score:.2f}/100")
    print(f"Queries Generated: {len(result.simulated_queries)}")
    print(f"Mentions Found: {len(result.brand_mentions)}")
    print(f"Marketing Insights: {len(result.insights)}")
    print("\nSummary:")
    print(result.summary_markdown[:500] + "..." if len(result.summary_markdown) > 500 else result.summary_markdown)
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Run the BrandZero research pipeline")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--output", "-o", help="Output file path (JSON format)", default="analysis_result.json")
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Run the pipeline
    asyncio.run(run_pipeline(args.brand, args.output))

if __name__ == "__main__":
    main()
