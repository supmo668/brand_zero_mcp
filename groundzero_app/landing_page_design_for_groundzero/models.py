from pydantic import BaseModel
from typing import List, Optional


class ChannelScore(BaseModel):
    channel_name: str
    score: int
    explanation: str
    rank: Optional[int] = None


class BrandPresenceResult(BaseModel):
    category: str
    channel_name: str
    score: int
    explanation: str
    rank: Optional[int] = None


class LLMQuery(BaseModel):
    brand_name: str
    channels_to_query: List[str]


class LLMResponse(BaseModel):
    brand_name: str
    results: List[BrandPresenceResult]
    summary: Optional[str] = None
    overall_score: Optional[int] = None