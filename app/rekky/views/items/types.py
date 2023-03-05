from typing import List, Union

from pydantic.main import BaseModel

from rekky.recommender.types import Item


class ItemsIngestRequest(BaseModel):
    items: List[Item]
    collection: str


class ItemsDeletionRequest(BaseModel):
    ids: List[Union[int, str]]
    collection: str


class CollectionItemsResetRequest(BaseModel):
    collection: str


class ItemsIngestResponse(BaseModel):
    message: str


class ItemsDeletionResponse(BaseModel):
    message: str


class CollectionItemsResetResponse(BaseModel):
    message: str
