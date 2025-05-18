from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Query(BaseModel):
    """A simulated consumer query without direct brand mention"""
    text: str = Field(..., description="The simulated query text")
    context: str = Field(..., description="The reasoning behind generating this query")

class LLMSource(BaseModel):
    """A source found by an LLM during research"""
    url: str = Field(..., description="The URL of the source")
    title: str = Field(default="", description="The title of the source page")
    snippet: str = Field(..., description="Relevant excerpt from the source")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this source was retrieved")

class SearchResult(BaseModel):
    """Search results from a specific LLM"""
    llm_name: str = Field(..., description="Name of the LLM that produced these results")
    query: str = Field(..., description="The query that produced these results")
    sources: List[LLMSource] = Field(default_factory=list, description="List of sources found")
    raw_response: str = Field(..., description="The complete response from the LLM")

class BrandMention(BaseModel):
    """Analysis of a brand mention in a source"""
    source_url: str = Field(..., description="URL where the brand was mentioned")
    context: str = Field(..., description="The context in which the brand was mentioned")
    sentiment: str = Field(..., description="Positive, negative, or neutral sentiment")
    competitors: List[str] = Field(default_factory=list, description="Competitor brands mentioned in the same context")

class MarketingInsight(BaseModel):
    """Valuable marketing insight derived from the analysis"""
    category: str = Field(..., description="Category of insight: competitor, sentiment, visibility, etc.")
    description: str = Field(..., description="Detailed description of the insight")
    evidence_urls: List[str] = Field(default_factory=list, description="URLs supporting this insight")
    priority: int = Field(1, ge=1, le=5, description="Priority level of this insight (1-5)")

class BrandAnalysisResult(BaseModel):
    """Complete analysis result for a brand"""
    brand_name: str = Field(..., description="Name of the brand being analyzed")
    simulated_queries: List[Query] = Field(..., description="List of simulated consumer queries")
    search_results: List[SearchResult] = Field(..., description="Results from all LLM searches")
    brand_mentions: List[BrandMention] = Field(..., description="Analysis of brand mentions")
    insights: List[MarketingInsight] = Field(..., description="Key marketing insights")
    visibility_score: float = Field(..., ge=0, le=100, description="Overall brand visibility score (0-100)")
    summary_markdown: str = Field(..., description="Markdown formatted summary of findings")
