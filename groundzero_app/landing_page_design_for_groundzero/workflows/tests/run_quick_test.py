#!/usr/bin/env python
"""
Quick test script to demonstrate running the BrandZero pipeline
This simplified version runs just the query simulation and search steps
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import BrandResearchPipeline
from models import Query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_quick_test(brand_name):
    """Run a simplified test of just query generation and search"""
    logger.info(f"Starting quick test for brand: {brand_name}")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize the pipeline
    pipeline = BrandResearchPipeline()
    
    # Step 1: Generate queries
    logger.info("Generating simulated consumer queries...")
    queries = await pipeline.generate_queries(brand_name)
    
    logger.info(f"Generated {len(queries)} queries:")
    for i, query in enumerate(queries[:3], 1):  # Show first 3 queries
        logger.info(f"  {i}. {query.text} - Context: {query.context}")
    if len(queries) > 3:
        logger.info(f"  ... and {len(queries) - 3} more")
    
    # Step 2: Run searches (limit to first 2 queries for quick testing)
    test_queries = queries[:2]
    logger.info(f"Searching with {len(test_queries)} queries...")
    search_results = await pipeline.search_with_llms(test_queries)
    
    logger.info(f"Got {len(search_results)} search results")
    
    # Save results to output file
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_quick_test.json")
    
    results = {
        "brand_name": brand_name,
        "timestamp": datetime.now().isoformat(),
        "queries": [q.dict() for q in queries],
        "search_results": [r.dict() for r in search_results]
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nQuick test completed successfully!")
    print(f"Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_quick_test.py <brand_name>")
        sys.exit(1)
    
    brand_name = sys.argv[1]
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required.")
        print("Please create a .env file from .env.template and add your API keys.")
        sys.exit(1)
    
    asyncio.run(run_quick_test(brand_name))
