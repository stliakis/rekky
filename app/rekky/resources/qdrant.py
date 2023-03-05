from qdrant_client import QdrantClient

from rekky.settings import get_settings


def get_qdrant():
    return QdrantClient(url=get_settings().QDRANT_HOST)
