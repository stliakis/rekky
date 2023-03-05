from rekky.recommender.embeddings import OpenAiEmbeddingsCalculator
from rekky.recommender.similarity_engine import SimilarityEngine
from rekky.settings import get_settings
from rekky.views.items.types import ItemsIngestRequest, ItemsDeletionRequest, CollectionItemsResetRequest, \
    ItemsIngestResponse, ItemsDeletionResponse, CollectionItemsResetResponse
from rekky.tasks.items import ingest_items, delete_items
from more_itertools import batched
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/api/items", response_model=ItemsIngestResponse)
def items_ingest(ingest_request: ItemsIngestRequest) -> ItemsIngestResponse:
    if len(ingest_request.items) > 100000:
        raise HTTPException(status_code=422,
                            detail="Too many items to ingest at once. Please use batches of 100000 items.")

    for batch in batched(ingest_request.items, get_settings().INGEST_BATCH_SIZE):
        ingest_items.delay(ingest_request.collection, batch)
    return ItemsIngestResponse(message=f"Scheduled {len(ingest_request.items)} items for ingestion")


@router.delete("/api/items", response_model=ItemsDeletionResponse)
def items_delete(delete_request: ItemsDeletionRequest) -> ItemsDeletionResponse:
    for batch in batched(delete_request.ids, get_settings().DELETE_BATCH_SIZE):
        delete_items.delay(delete_request.collection, batch)

    return ItemsDeletionResponse(message=f"Scheduled {len(delete_request.ids)} items for deletion")


@router.delete("/api/collection/items", response_model=CollectionItemsResetResponse)
def collection_items_delete(delete_request: CollectionItemsResetRequest) -> CollectionItemsResetResponse:
    similarity_engine = SimilarityEngine(delete_request.collection, embeddings_calculator=OpenAiEmbeddingsCalculator())

    similarity_engine.delete_all()

    return CollectionItemsResetResponse(message=f"Collection {delete_request.collection} items have been flushed")
