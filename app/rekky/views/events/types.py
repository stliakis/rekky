from typing import List, Union

from pydantic.main import BaseModel

from rekky.recommender.types import Item, Event


class EventsIngestRequest(BaseModel):
    events: List[Event]
    collection: str


class CollectionEventsResetRequest(BaseModel):
    collection: str


class EventsIngestResponse(BaseModel):
    message: str


class CollectionEventsResetResponse(BaseModel):
    message: str
