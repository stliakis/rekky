from rekky.recommender.collaborative_engine import CollaborativeEngine
from rekky.recommender.embeddings import OpenAiEmbeddingsCalculator
from rekky.recommender.similarity_engine import SimilarityEngine
from rekky.recommender.types import RecommendationConfig, Recommendation
from rekky.utils import uuid_or_int


class Recommender(object):
    def __init__(self, collection: str, config: RecommendationConfig):
        self.collection = collection
        self.config = config
        self.collaborative_engine = CollaborativeEngine(collection)
        self.similarity_engine = SimilarityEngine(collection, OpenAiEmbeddingsCalculator())

    def recommend(self) -> Recommendation:
        if self.config.similarity:
            items = self.similarity_engine.get_similar_to_query_vector(
                query_vector=self.similarity_engine.get_query_vector(
                    properties=self.config.similarity.similar_to_properties,
                    item_id=self.config.similarity.similar_to_item
                ),
                limit=self.config.limit,
                offset=self.config.offset,
                exclude_ids=list(map(uuid_or_int, self.config.similarity.exclude_ids or [])),
                filter=self.config.similarity.filter
            )

            return Recommendation(
                items=items
            )

        elif self.config.collaborative:
            items = self.collaborative_engine.get_items_seen_by_others(
                item_ids=self.config.collaborative.item_ids,
                limit=self.config.limit,
            )

            return Recommendation(
                items=items
            )
        elif self.config.combined:
            raise NotImplementedError()
