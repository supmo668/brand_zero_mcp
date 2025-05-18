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
    presence_score: int = Field(
        default=0,
        ge=0,  # Score must be greater than or equal to 0
        le=100,  # Score must be less than or equal to 100
        description="Brand presence score out of 100, indicating overall visibility and strength in search results. 0 means no presence, 100 means dominant presence."
    )
    competitors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of competitor brands found in search results with their relative presence."
    )
    sentiment: str = Field(
        default="",
        description="Overall consumer sentiment about the brand (positive, negative, neutral, or mixed)."
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Strategic recommendations for improving brand visibility and presence."
    )
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom method to ensure proper JSON serialization."""
        return super().model_dump_json(**kwargs)
        
    @classmethod
    def parse_raw(cls, json_str: str) -> "BrandAnalysisResult":
        """Parse from raw JSON string."""
        return cls.model_validate_json(json_str)

class TransformationState(BaseModel):
    """State object for the reformulation process."""
    brand_or_product: str
    score: int = Field(default=0, ge=0, le=100, description="Score indicating the quality of the analysis.")
    simulated_queries: List[SimulatedQuery] = Field(default_factory=list)
    search_results: List[SearchResult] = Field(default_factory=list)
    analysis_result: Optional[BrandAnalysisResult] = None
    intermediate_steps: List[IntermediateStep] = Field(default_factory=list)
    context: Dict[str, List[str]] = Field(default_factory=dict)
    error: Optional[str] = None
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Custom method to ensure proper serialization."""
        return super().model_dump(**kwargs)
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom method to ensure proper JSON serialization."""
        return super().model_dump_json(**kwargs)
        
    @classmethod
    def parse_raw(cls, json_str: str) -> "TransformationState":
        """Parse from raw JSON string."""
        return cls.model_validate_json(json_str)
