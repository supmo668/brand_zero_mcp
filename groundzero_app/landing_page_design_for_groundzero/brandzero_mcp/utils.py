"""
Utility functions for the Brand Zero MCP application.
"""
import re
import json
import yaml
from typing import Dict, Any, Tuple, Optional, List

import logging
logger = logging.getLogger("brand_zero.utils")

# Load configuration
import os
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(config_path, "r") as f:
    CONFIG = yaml.safe_load(f)

def extract_json_from_text(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Extract JSON from text that may contain non-JSON content.
    
    Args:
        text: The text potentially containing JSON
        
    Returns:
        Tuple of (extracted JSON as dict or None if extraction failed, remaining text)
    """
    # Try to find JSON within markdown code blocks
    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    code_blocks = re.findall(code_block_pattern, text)
    
    # Try each code block for valid JSON
    for block in code_blocks:
        try:
            json_data = json.loads(block.strip())
            # Remove the JSON block from the text
            remaining_text = text.replace(f"```json\n{block}\n```", "", 1)
            remaining_text = remaining_text.replace(f"```\n{block}\n```", "", 1)
            return json_data, remaining_text.strip()
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON within the raw text using regex
    json_pattern = r"\{\s*\".*?\"\s*:[\s\S]*?\}"
    json_match = re.search(json_pattern, text)
    if json_match:
        try:
            json_text = json_match.group(0)
            json_data = json.loads(json_text)
            # Remove the JSON from the text
            remaining_text = text.replace(json_text, "", 1)
            return json_data, remaining_text.strip()
        except json.JSONDecodeError:
            pass
    
    # If no JSON found in code blocks or raw text, try the entire text
    try:
        json_data = json.loads(text)
        return json_data, ""
    except json.JSONDecodeError:
        return None, text

def extract_urls_from_markdown(markdown_text: str) -> List[str]:
    """
    Extract URLs from markdown text.
    
    Args:
        markdown_text: The markdown text
        
    Returns:
        List of URLs
    """
    # Match markdown links [text](url)
    md_link_pattern = r'\[(?:[^\]]*)\]\(([^)]+)\)'
    md_links = re.findall(md_link_pattern, markdown_text)
    
    # Match raw URLs
    url_pattern = r'(?<!\()(https?://[^\s\)]+)'
    raw_urls = re.findall(url_pattern, markdown_text)
    
    # Combine and remove duplicates while preserving order
    all_urls = []
    for url in md_links + raw_urls:
        if url not in all_urls:
            all_urls.append(url)
    
    return all_urls

def format_sources_for_prompt(sources: List[Dict[str, str]]) -> str:
    """
    Format search result sources for inclusion in a prompt.
    
    Args:
        sources: List of source dictionaries with url, title, snippet
        
    Returns:
        Formatted string of sources
    """
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        title = source.get("title", "No title")
        url = source.get("url", "No URL")
        snippet = source.get("snippet", "No content")
        
        formatted_source = f"SOURCE {i}:\n"
        formatted_source += f"Title: {title}\n"
        formatted_source += f"URL: {url}\n"
        formatted_source += f"Content: {snippet}\n"
        formatted_sources.append(formatted_source)
    
    return "\n\n".join(formatted_sources)
