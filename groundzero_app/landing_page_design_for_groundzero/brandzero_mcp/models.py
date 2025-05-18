"""
Data models for the Brand Zero MCP application.
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class StepStatus(str, Enum):
    """Status of an analysis step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class IntermediateStep(BaseModel):
    """Represents an intermediate step in the analysis pipeline."""
    step_name: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Dict[str, Any] = {}
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SimulatedQuery(BaseModel):
    """A simulated search query."""
    query: str
    
class SearchResult(BaseModel):
    """Result from a search provider."""
    query: str
    provider: str
    content: str
    sources: List[Dict[str, str]] = Field(default_factory=list)

class BrandAnalysisResult(BaseModel):
    """Analysis result from the judge."""
    brand_name: str
    frequency: int
    summary: str
    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    sentiment: str
    recommendations: List[str] = Field(default_factory=list)

class TransformationState(BaseModel):
    """State object for the reformulation process."""
    brand_or_product: str
    simulated_queries: List[SimulatedQuery] = Field(default_factory=list)
    search_results: List[SearchResult] = Field(default_factory=list)
    analysis_result: Optional[BrandAnalysisResult] = None
    intermediate_steps: List[IntermediateStep] = Field(default_factory=list)
    context: Dict[str, List[str]] = Field(default_factory=dict)
    error: Optional[str] = None
