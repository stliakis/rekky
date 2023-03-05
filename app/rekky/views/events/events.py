from rekky.recommender.collaborative_engine import CollaborativeEngine
from rekky.settings import get_settings
from rekky.views.events.types import EventsIngestRequest, CollectionEventsResetRequest, EventsIngestResponse, \
    CollectionEventsResetResponse
from rekky.tasks.events import ingest_events
from more_itertools import batched
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/api/events", response_model=EventsIngestResponse)
def events_ingest(ingest_request: EventsIngestRequest) -> EventsIngestResponse:
    if len(ingest_request.events) > 1000000:
        raise HTTPException(status_code=422,
                            detail="Too many events to ingest at once. Please use batches of 1000000 events.")

    for batch in batched(ingest_request.events, get_settings().INGEST_BATCH_SIZE):
        ingest_events.delay(ingest_request.collection, batch)

    return EventsIngestResponse(message=f"Scheduled {len(ingest_request.events)} events for ingestion")


@router.delete("/api/collection/events", response_model=CollectionEventsResetResponse)
def events_delete(delete_request: CollectionEventsResetRequest) -> CollectionEventsResetResponse:
    collaborative_engine = CollaborativeEngine(delete_request.collection)
    collaborative_engine.create_collection(force=True)

    return CollectionEventsResetResponse(message=f"Collection {delete_request.collection} events have been flushed")
