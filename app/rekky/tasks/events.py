from typing import List, Union

from rekky.celery_app import celery_app
from rekky.recommender.collaborative_engine import CollaborativeEngine
from rekky.recommender.embeddings import OpenAiEmbeddingsCalculator
from rekky.recommender.types import Item, Event
from rekky.settings import get_settings
from rekky.recommender.similarity_engine import SimilarityEngine


@celery_app.task
def ingest_events(collection: str, events: List[Event]):
    collaborative_engine = CollaborativeEngine(collection)
    collaborative_engine.ingest(events)
