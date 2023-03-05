from typing import List, Union

from rekky.celery_app import celery_app
from rekky.recommender.embeddings import OpenAiEmbeddingsCalculator
from rekky.recommender.types import Item
from rekky.settings import get_settings
from rekky.recommender.similarity_engine import SimilarityEngine


@celery_app.task
def ingest_items(collection: str, items: List[Item]):
    similarity_engine = SimilarityEngine(collection, embeddings_calculator=OpenAiEmbeddingsCalculator())

    similarity_engine.ingest(items)


@celery_app.task
def delete_items(collection: str, ids: List[Union[str, int]]):
    similarity_engine = SimilarityEngine(collection, embeddings_calculator=OpenAiEmbeddingsCalculator())

    similarity_engine.delete_items(ids)
