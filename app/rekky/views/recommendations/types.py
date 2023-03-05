from typing import Union, List, Optional

from pydantic.main import BaseModel

from rekky.recommender.types import RecommendationConfig, RecommendedItem


class RecommendRequest(BaseModel):
    collection: str
    config: RecommendationConfig


class RecommendResponse(BaseModel):
    items: Optional[List[RecommendedItem]]
    error: Optional[str]
