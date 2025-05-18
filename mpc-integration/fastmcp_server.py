"""FastMCP server with brand tool."""

from typing import Any, Dict, List, Optional
import httpx
import asyncio
import inspect
import subprocess

class FastMCP:
    """FastMCP server with brand tool."""
    
    def __init__(self, name: str):
        """Initialize the FastMCP server."""
        self.name = name
        self.tools = {}
    
    def tool(self):
        """Decorator to register a tool."""
        def decorator(func):
            signature = inspect.signature(func)
            parameters = {}
            required = []
            
            for name, param in signature.parameters.items():
                param_type = param.annotation
                if param_type is inspect.Parameter.empty:
                    param_type = str
                
                if param_type is int:
                    param_schema = {"type": "integer"}
                elif param_type is float:
                    param_schema = {"type": "number"}
                elif param_type is bool:
                    param_schema = {"type": "boolean"}
                else:
                    param_schema = {"type": "string"}
                
                # Add description if available from docstring
                if func.__doc__:
                    for line in func.__doc__.split("\n"):
                        line = line.strip()
                        if line.startswith(f"{name}:"):
                            param_schema["description"] = line[len(name)+1:].strip()
                
                parameters[name] = param_schema
                if param.default is inspect.Parameter.empty:
                    required.append(name)
            
            # Create tool schema
            tool_schema = {
                "name": func.__name__,
                "description": func.__doc__.split("\n")[0] if func.__doc__ else "",
                "inputSchema": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
            
            self.tools[func.__name__] = {
                "schema": tool_schema,
                "func": func
            }
            return func
        return decorator
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [tool["schema"] for tool in self.tools.values()]
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Call a tool by name with arguments."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        return await tool["func"](**args)


# Initialize FastMCP server
mcp = FastMCP("brand")
from .brandzero_workflow import (
    run_workflow, BrandAnalysisResult, TransformationState
)
@mcp.tool()
async def get_brand(command: str) -> str:
    """Get brand analytics and competitive information.
    
    command: The brand name to analyze
    """
    result: BrandAnalysisResult = run_workflow(brand_or_product=command)
    
    return result.model_dump() if result else {}
f"""
Brand Analytics Report:
---------------------
Brand Score: {mock_data['brand_score']}/100
Visibility Ranking: #{mock_data['visibility_rank']} in industry
Market Share: {mock_data['market_share']}

Social Media Presence:
- Total Followers: {mock_data['social_media_presence']['followers']}
- Engagement Rate: {mock_data['social_media_presence']['engagement_rate']}
- Brand Sentiment: {mock_data['social_media_presence']['sentiment']}

Key Metrics:
- Brand Awareness: {mock_data['key_metrics']['brand_awareness']}
- Customer Satisfaction: {mock_data['key_metrics']['customer_satisfaction']}
- Brand Loyalty: {mock_data['key_metrics']['brand_loyalty']}
- Market Growth: {mock_data['key_metrics']['market_growth']}

Top Competitors:
{chr(10).join([f"- {comp['name']}: {comp['market_share']} market share, Brand Score: {comp['brand_score']}/100" for comp in mock_data['competitors']])}
"""
