#!/usr/bin/env python
# filepath: c:\Users\mo\Documents\GitHub\Projects\Hackathon\brandZero\tests\test_langgraph.py

import asyncio
import json
import logging
import os
import sys
import argparse
from pprint import pprint
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import BrandResearchPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_langgraph(brand_name: str, output_dir: str = None, debug: bool = False):
    """
    Test the LangGraph pipeline execution
    """
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Testing LangGraph pipeline for brand: {brand_name}")
    
    try:
        # Initialize the pipeline
        pipeline = BrandResearchPipeline()
        
        # Build the graph
        graph = pipeline.build_graph()
        
        # Define callback to track progress if debug is enabled
        node_outputs: Dict[str, Any] = {}
        
        if debug:
            async def debug_callback(state):
                step = state.get("__run_state", {}).get("step", "unknown")
                result = state.get("__run_state", {}).get("node_result")
                
                if step and result is not None:
                    node_outputs[step] = result
                    logger.info(f"Step completed: {step}")
            
            trace_config = {"on_state_update": debug_callback}
        else:
            trace_config = {}
        
        # Execute the graph
        logger.info("Executing LangGraph pipeline...")
        result = await graph.ainvoke(
            {
                "brand_name": brand_name,
                "state": {}
            },
            config=trace_config
        )
        
        # Save the result
        output_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_langgraph_result.json")
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"LangGraph results saved to {output_file}")
        
        # If debug mode, save individual node outputs
        if debug and node_outputs:
            debug_file = os.path.join(output_dir, f"{brand_name.replace(' ', '_')}_langgraph_debug.json")
            with open(debug_file, 'w') as f:
                json.dump(node_outputs, f, indent=2)
            logger.info(f"Debug outputs saved to {debug_file}")
        
        # Print summary
        print("\n" + "="*50)
        print(f"LANGGRAPH PIPELINE RESULTS: {brand_name}")
        print("="*50)
        print(f"Queries Generated: {len(result.get('queries', []))}")
        print(f"Search Results: {len(result.get('search_results', []))}")
        if 'visibility_score' in result:
            print(f"Visibility Score: {result['visibility_score']:.2f}")
        print(f"Results saved to: {output_file}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing LangGraph pipeline: {str(e)}")
        raise

def main():
    """
    Main entry point for the test script
    """
    parser = argparse.ArgumentParser(description="Test the LangGraph pipeline")
    parser.add_argument("brand", help="Brand or product name to analyze")
    parser.add_argument("--output-dir", "-o", help="Output directory for results", default=None)
    parser.add_argument("--debug", "-d", help="Enable debug mode with detailed outputs", action="store_true")
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if not os.environ.get("PERPLEXITY_API_KEY"):
        logger.warning("PERPLEXITY_API_KEY environment variable is not set. Some features may not work correctly.")
    
    # Run the test
    asyncio.run(test_langgraph(args.brand, args.output_dir, args.debug))

if __name__ == "__main__":
    main()
