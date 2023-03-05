from datetime import datetime
from typing import Union, List, Optional

import json

from pydantic.fields import Field
from pydantic.main import BaseModel

from rekky.utils import uuid_or_int
import hashlib


class Item(BaseModel):
    id: Union[str, int]
    properties: dict[str, Union[str, int, float, bool, None, List[Union[str, int, float, bool, None]]]]

    def get_id(self):
        return uuid_or_int(self.id)

    def get_properties_with_hash(self):
        return {
            **self.properties,
            "_hash": self.get_hash()
        }

    def get_hash(self):
        return hashlib.md5(f"${json.dumps(self.properties)}".encode("utf-8")).hexdigest()

    @classmethod
    def from_qdrant_item(cls, qdrant_item):
        return cls(id=qdrant_item.id, properties={k: v for k, v in qdrant_item.payload.items() if k != "_hash"})


class RecommendedItem(BaseModel):
    item: Item
    score: float


class Event(BaseModel):
    event: str
    date: datetime = Field(default_factory=datetime.now)
    user_id: Union[str, int]
    item_id: Union[str, int]


class Recommendation(BaseModel):
    items: List[RecommendedItem]


class CombinedRecommendationConfig(BaseModel):
    pass


class SimilarityRecommendationConfig(BaseModel):
    similar_to_properties: dict[str, Union[str, int, None, bool, float]] = None
    similar_to_item: Union[str, int] = None
    filter: dict[str, Union[str, int, float, bool]] = None
    exclude_ids: List[Union[str, int]] = None


class CollaborativeRecommendationConfig(BaseModel):
    item_ids: List[Union[str, int]]


class RecommendationConfig(BaseModel):
    combined: Optional[CombinedRecommendationConfig] = None
    similarity: Optional[SimilarityRecommendationConfig] = None
    collaborative: Optional[CollaborativeRecommendationConfig] = None
    limit: int = 10
    offset: int = 0
