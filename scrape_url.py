# Install with pip install firecrawl-py
import asyncio
from firecrawl import AsyncFirecrawlApp
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    app = AsyncFirecrawlApp(api_key=os.environ.get("FIRECRAWL_API_KEY"))
    response = await app.scrape_url(
        url='agihouse.org/',		
        formats= [ 'markdown' ],
        only_main_content= True
    )
    print(response)

asyncio.run(main())