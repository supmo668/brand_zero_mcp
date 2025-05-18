#!/usr/bin/env python
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\tests\test_pipeline.py

import asyncio
import json
import logging
import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import BrandResearchPipeline
from models import BrandAnalysisResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'test_pipeline.log'))
    ]
)
logger = logging.getLogger(__name__)

async def run_test_pipeline(brand_name: str, output_dir: str = None):
    """
    Run the brand research pipeline as a test
    """
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Starting test pipeline for brand: {brand_name}")
    
    try:
        # Initialize the pipeline
        pipeline = BrandResearchPipeline()
        
        # Run the analysis
        logger.info("Running brand analysis...")
        start_time = datetime.now()
        result = await pipeline.run_analysis(brand_name)
        end_time = datetime.now()
        
        # Calculate duration
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Analysis completed in {duration:.2f} seconds")
        
        # Save results
        output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_analysis.json")
        logger.info(f"Saving results to {output_file}")
        
        with open(output_file, 'w') as f:
            json.dump(result.dict(), f, indent=2)
        
        # Save markdown summary separately
        markdown_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_summary.md")
        with open(markdown_file, 'w') as f:
            f.write(result.summary_markdown)
            
        logger.info(f"Markdown summary saved to {markdown_file}")
        
        # Print summary info
        print("\n" + "="*50)
        print(f"BRAND ANALYSIS RESULTS: {brand_name}")
        print("="*50)
        print(f"Visibility Score: {result.visibility_score:.2f}/100")
        print(f"Queries Generated: {len(result.simulated_queries)}")
        print(f"Sources Analyzed: {sum(len(r.sources) for r in result.search_results)}")
        print(f"Brand Mentions Found: {len(result.brand_mentions)}")
        print(f"Marketing Insights: {len(result.insights)}")
        print("\nResults saved to:")
        print(f"- Full data: {output_file}")
        print(f"- Markdown summary: {markdown_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error running test pipeline: {str(e)}")
        raise

def main():
    """
    Main entry point for the test script
    """
    parser = argparse.ArgumentParser(description="Test the BrandZero research pipeline")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--output-dir", "-o", help="Output directory for results", default=None)
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if not os.environ.get("PERPLEXITY_API_KEY"):
        logger.warning("PERPLEXITY_API_KEY environment variable is not set. Some features may not work correctly.")
    
    # Run the test pipeline
    asyncio.run(run_test_pipeline(args.brand, args.output_dir))

if __name__ == "__main__":
    main()
