import os
import sys
import json
import requests
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_queries(
    brand: str,
    persona: str,
    context: str,
    num_queries: int = 5,
    api_key: Optional[str] = None,
    model: str = os.environ.get("LLM_MODEL_NAME")
) -> List[str]:
    """
    Generate queries that a specific persona might ask about a brand/URL using Grok API.
    
    Args:
        brand: The brand name or URL to generate queries about
        persona: Description of the persona who would ask the queries
        num_queries: Number of queries to generate (default: 5)
        api_key: Grok API key (defaults to environment variable)
        model: The Grok model to use
        
    Returns:
        List of generated queries
    """
    # Set up API key
    if api_key is None:
        api_key = os.environ.get("LLM_API_KEY")
    
    if not api_key:
        raise ValueError("Grok API key is required. Either pass it as api_key or set LLM_API_KEY environment variable.")
    
    # Craft the prompt
    prompt = f"""You are an expert at understanding how different personas think and what questions they might ask about brands or products.

Brand/URL: {brand}
Context: {context}
Persona: {persona}

Generate {num_queries} realistic and diverse queries that this persona would likely ask to an AI assistant about this brand/product given the context. 
The queries should:
- Generaize the cateogry of the brand / product. 
- Generate the queries that person would ask in this domain. 
- Should not include the product / service name in the query
- Generarize and generate the queries that person would ask in this domain. 
- Reflect the persona's interests, knowledge level, and concerns
- Be phrased naturally as the persona would ask them
- Include specific details when relevant
- Be distinct from each other

Format your response as a JSON array of strings, with each string being a query.
"""

    # Call Grok API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates realistic queries."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        # Assuming Grok API endpoint (adjust as needed)
        llm_api_url = os.environ.get("LLM_API_ENDPOINT", "https://api.x.ai/v1/chat/completions")
        response = requests.post(llm_api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        
        # Extract content from Grok response
        # Note: Adjust based on actual Grok API response format
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        results = json.loads(content)
        
        # Handle different possible JSON structures
        if isinstance(results, dict) and "queries" in results:
            queries = results["queries"]
        elif isinstance(results, dict) and any(k.lower().startswith("quer") for k in results.keys()):
            # Find the first key that starts with "quer"
            key = next(k for k in results.keys() if k.lower().startswith("quer"))
            queries = results[key]
        elif isinstance(results, list):
            queries = results
        else:
            # If we can't find a proper structure, grab all string values
            queries = [v for v in results.values() if isinstance(v, str)]
            
        # Ensure we have the right number of queries
        queries = queries[:num_queries]
        
        return queries
    except Exception as e:
        raise ValueError(f"Failed to generate queries using Grok API: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Example: Generate queries about AGI House from a technical professional's perspective
    try:
        queries = generate_queries(
            brand="AGI House",
            context="AGI House is a community, fellowship, and VC fund empowering the world's most talented AI founders and researchers, located in  Hillsborough, CA",
            persona="Technical professional interested in AI development",
            num_queries=5
        )
        
        print(f"Generated queries about AGI House:")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Set your LLM_API_KEY environment variable or pass it as a parameter.")
