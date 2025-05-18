"""
LLM providers for the Brand Zero MCP application.
"""
import os
import asyncio
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_perplexity import ChatPerplexity
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

import logging
logger = logging.getLogger("brand_zero.llm_providers")

from utils import CONFIG

class BaseSearchProvider:
    """Base class for search providers."""
    
    def __init__(self):
        self.name = "base"
        
    async def search(self, query: str) -> Dict[str, Any]:
        """Search for query."""
        raise NotImplementedError("Subclasses must implement search.")

class OpenAISearchProvider(BaseSearchProvider):
    """OpenAI search provider."""
    
    def __init__(self):
        self.name = "openai"
        self.model_name = CONFIG["models"].get("OPENAI_MODEL", "gpt-4o")
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable must be set")
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            temperature=0.0
        )
        logger.info(f"Initialized OpenAI search provider with model {self.model_name}")
        
    async def search(self, query: str) -> Dict[str, Any]:
        """Search with OpenAI."""
        try:
            system_message = SystemMessage(
                content="You are a helpful research assistant that provides information with sources."
            )
            human_message = HumanMessage(content=query)
            response = await self.llm.ainvoke([system_message, human_message])
            
            # Extract sources from the response
            # This will work with gpt-4o-search-preview which includes sources
            sources = []
            content = response.content
            
            # OpenAI search model includes sources at the end of the response
            # We'll parse them with a simple heuristic
            if "Sources:" in content:
                main_content, sources_text = content.split("Sources:", 1)
                
                # Extract source URLs from the sources section
                source_items = sources_text.strip().split("\n")
                for item in source_items:
                    if item.strip() and "http" in item:
                        # Basic parsing of sources
                        try:
                            parts = item.split(":", 1)
                            if len(parts) == 2:
                                title = parts[0].strip()
                                url = parts[1].strip()
                            else:
                                title = "Source"
                                url = item.strip()
                                
                            sources.append({
                                "title": title,
                                "url": url,
                                "snippet": f"From {title}"
                            })
                        except Exception as e:
                            logger.error(f"Error parsing source {item}: {e}")
                
                # Update content to exclude the sources section
                content = main_content.strip()
            
            return {
                "provider": self.name,
                "content": content,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"OpenAI search error: {e}")
            return {
                "provider": self.name,
                "content": f"Error performing search: {str(e)}",
                "sources": []
            }

class PerplexitySearchProvider(BaseSearchProvider):
    """Perplexity search provider."""
    
    def __init__(self):
        self.name = "perplexity"
        self.model_name = CONFIG["models"].get("PERPLEXITY_MODEL", "sonar-pro")
        self.api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.error("PERPLEXITY_API_KEY environment variable must be set")
            raise ValueError("PERPLEXITY_API_KEY environment variable must be set")
        
        self.llm = ChatPerplexity(
            model=self.model_name,
            pplx_api_key=self.api_key,
            temperature=0.0
        )
        logger.info(f"Initialized Perplexity search provider with model {self.model_name}")
        
    async def search(self, query: str) -> Dict[str, Any]:
        """Search with Perplexity."""
        try:
            system_message = SystemMessage(
                content="You are a helpful research assistant. Please provide information with sources."
            )
            human_message = HumanMessage(content=query)
            response = await self.llm.ainvoke([system_message, human_message])
            
            # Extract sources from the response
            content = response.content
            sources = []
            
            # Perplexity usually includes sources at the end of the response
            if "Sources:" in content or "SOURCES:" in content:
                # Split by Sources: or SOURCES:
                parts = content.split("Sources:", 1) if "Sources:" in content else content.split("SOURCES:", 1)
                if len(parts) == 2:
                    main_content = parts[0].strip()
                    sources_text = parts[1].strip()
                    
                    # Extract sources using simple heuristics
                    source_lines = sources_text.split("\n")
                    for line in source_lines:
                        if "http" in line:
                            try:
                                # Try to extract URL and title
                                if "[" in line and "]" in line and "(" in line and ")" in line:
                                    # Markdown format [title](url)
                                    title = line.split("[", 1)[1].split("]", 1)[0]
                                    url = line.split("(", 1)[1].split(")", 1)[0]
                                else:
                                    # Plain URL or other format
                                    title = "Source"
                                    url = line.strip()
                                    for prefix in ["- ", "* ", "• "]:
                                        if url.startswith(prefix):
                                            url = url[len(prefix):].strip()
                                
                                sources.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": f"From {title}"
                                })
                            except Exception as e:
                                logger.error(f"Error parsing source line {line}: {e}")
                    
                    # Update content to exclude the sources section
                    content = main_content
            
            return {
                "provider": self.name,
                "content": content,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Perplexity search error: {e}")
            return {
                "provider": self.name,
                "content": f"Error performing search: {str(e)}",
                "sources": []
            }
