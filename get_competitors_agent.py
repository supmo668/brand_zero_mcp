"""
1. Run (query) through each LLM
2. Get source URLs and then parse out competitor information
3. Return everything to the next step
"""

import os
import pdb
import asyncio
import pandas as pd

from openai import OpenAI
from brand_zero_mcp.get_competitor_prompts import RESPONSE_AGENT, EXTRACTION_AGENT

from firecrawl import AsyncFirecrawlApp

# Replace with your actual API keys in environment variables
os.environ["OPENAI_API_KEY"] = ""
os.environ["PERPLEXITY_API_KEY"] = ""
os.environ["FIRECRAWL_API_KEY"] = ""

def make_perplexity_api_call(query, system_prompt, model_name) -> dict:
    client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai")

    messages = [
        {
            "role": "system",
            "content": (
                system_prompt
            ),
        },
        {   
            "role": "user",
            "content": (
                query
            ),
        },
    ]

    # chat completion without streaming
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )

    return response

def make_openai_api_call(query, system_prompt, model_name) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        }
    )

    return response

def run_agent(query, system_prompt, llm_name) -> dict:
    response = None
    if 'gpt' in llm_name:
        response = make_openai_api_call(query, system_prompt, model_name=llm_name)
    elif 'sonar' in llm_name:
        response = make_perplexity_api_call(query, system_prompt, model_name=llm_name)

    return response

def extract_urls_from_response(response: dict, llm: str) -> list:
    if 'sonar' in llm:
        urls = [{"title": "", "url": cit} for cit in response.citations]
        return urls
    
    urls = []
    
    # Check if the response contains annotations
    if not hasattr(response.choices[0].message, 'annotations'):
        print("No annotations found in the response.")
        return urls
    
    # Extract URLs from the annotations
    for annotation in response.choices[0].message.annotations:
        title = annotation.url_citation.title
        url = annotation.url_citation.url

        urls.append({
            "title": title,
            "url": url
        })

    return urls

async def scrape_urls(response_df):
    """Scrape all URLs in the dataframe asynchronously"""
    app = AsyncFirecrawlApp(api_key=os.environ.get("FIRECRAWL_API_KEY"))
    
    async def scrape_single_url(url: str):
        """Scrape a single URL and return the response"""
        try:
            # Properly await the coroutine
            response = await app.scrape_url(
                url=url,
                formats=['markdown'],
                only_main_content=True
            )
            return response
        except Exception as e:
            print(f"Error scraping URL {url}: {e}")
            return None
    
    # Create a list of tasks for all URLs
    tasks = []
    urls_to_scrape = []
    
    for index, row in response_df.iterrows():
        url = row['urls']
        urls_to_scrape.append((index, url))
        tasks.append(scrape_single_url(url))
    
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Update the dataframe with the results
    for (index, url), result in zip(urls_to_scrape, results):
        if result is not None:
            response_df.at[index, 'scraped_content'] = result.markdown
        else:
            response_df.at[index, 'scraped_content'] = "Failed to scrape"
    
    return response_df
    
# Example code to run the agent
async def main():
    # LLMs to query
    llms = [
        'gpt-4o-search-preview',
        # 'sonar',
    ]

    # Example queries
    queries = [
        "What are some notable communities or fellowships in the Bay Area that support AI researchers and startup founders with funding and networking opportunities?"
    ]

    # Create a dataframe to store LLM response and URLs
    response_df = pd.DataFrame(columns=["query", "llm", "response", "urls"])

    # STAGE 1: Run the agent for each query
    for llm in llms:
        for query in queries:
            print(f"\nRunning agent with query: '{query}' using LLM: {llm}")
            result = run_agent(query, RESPONSE_AGENT, llm)

            # Extract relevant information from the result
            urls = extract_urls_from_response(result, llm)

            # TODO: Now we scrape these URL pages and extract competitor information
            print("Extracted URLs:")
            for url in urls:
                print(f"Title: {url['title']}, URL: {url['url']}")
            
            # Store the result in the dataframe (each URL in a separate row)
            for url in urls:
                # Create a new row as a dictionary
                new_row = {
                    "query": query,
                    "llm": llm,
                    "response": result.choices[0].message.content,
                    "urls": url['url']
                }
                
                # Use concat instead of append
                response_df = pd.concat([response_df, pd.DataFrame([new_row])], ignore_index=True)
    
    # STAGE 2: Scrape the URLs asynchronously
    print("\nScraping URLs...")
    response_df = await scrape_urls(response_df)
    
    print("\nProcessing complete!")

    # STAGE 3: Extract competitor information from the scraped content
    for index, row in response_df.iterrows():
        scraped_content = row['scraped_content']
        query = row['query']

        llm_query = "QUERY: " + query + "\n\n" + "SCRAPED CONTENT: " + scraped_content
        
        # Run the extraction agent
        extraction_result = run_agent(llm_query, EXTRACTION_AGENT, llm_name='gpt-4o-mini')
        
        # Extract competitors from the scraped content
        competitors = extraction_result.choices[0].message.content
        
        # Store the competitors in the dataframe
        response_df.at[index, 'competitors'] = competitors

    return response_df

if __name__ == "__main__":
    # Run the async main function
    response_df = asyncio.run(main())
    
    # Now you can set a breakpoint for debugging
    pdb.set_trace()