from typing import List, Union
from qdrant_client.http import models as qdrant_models

from rekky.exceptions import ItemNotFound
from rekky.recommender.types import RecommendedItem, Item
from rekky.resources.qdrant import get_qdrant
from rekky.utils import uuid_or_int


class SimilarityEngine(object):
    def __init__(self, collection_name: str, embeddings_calculator):
        self.qdrant = get_qdrant()

        self.collection_name = collection_name
        self.embeddings_calculator = embeddings_calculator
        self.create_collection(force=False)

    def delete_all(self):
        self.create_collection(force=True)

    def delete_items(self, ids):
        self.qdrant.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.PointIdsList(
                points=list(map(uuid_or_int, ids))
            ),
        )

    def filter_out_ingested_items(
            self, items: List[Item]
    ) -> List[Item]:
        items_in_db = self.qdrant.retrieve(
            collection_name=self.collection_name,
            ids=[item.get_id() for item in items],
            with_payload=["_hash"],
        )

        hashes_in_db = [item.payload["_hash"] for item in items_in_db]

        changed_items = []
        for item in items:
            if item.get_hash() not in hashes_in_db:
                changed_items.append(item)

        return changed_items

    def get_query_vector(
            self,
            properties: dict = None,
            item_id: Union[str, int] = None,
            query_vector: List[int] = None,
    ):
        if properties:
            query_vector = self.embeddings_calculator.get_embeddings_from_properties(
                properties
            )
        elif item_id:
            item_id = uuid_or_int(item_id)

            items = self.qdrant.retrieve(
                collection_name=self.collection_name, ids=[item_id], with_vectors=True
            )

            if not items:
                raise ItemNotFound(self.collection_name, item_id)

            query_vector = items[0].vector
        elif not query_vector:
            raise Exception("Either properties or rekky_item must be provided")

        return query_vector

    def get_similar_to_query_vector(
            self,
            query_vector: List[int] = None,
            exclude_ids: List[Union[int, str]] = None,
            limit: int = 10,
            offset: int = 0,
            filter: Union[dict, None] = None,
            score_threshold=0.6,
    ):
        qdrant_filter = self.filter_to_qdrant_filter(filter or {})

        if exclude_ids:
            qdrant_filter.must_not.append(qdrant_models.HasIdCondition(has_id=exclude_ids))

        items = self.qdrant.search(
            collection_name=self.collection_name,
            search_params=qdrant_models.SearchParams(hnsw_ef=128, exact=False),
            query_vector=query_vector,
            limit=limit,
            offset=offset,
            query_filter=qdrant_filter,
            score_threshold=score_threshold,
        )

        return [
            RecommendedItem(
                item=Item(
                    id=item.id,
                    properties={k: v for k, v in item.payload.items() if k != "_hash"},
                ),
                score=item.score,
            )
            for item in items
        ]

    def ingest(self, items: List[Item]):
        changed_items = self.filter_out_ingested_items(items)

        if changed_items:
            print(f"ingesting {len(changed_items)} items")
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=qdrant_models.Batch(
                    ids=[item.get_id() for item in changed_items],
                    payloads=[
                        item.get_properties_with_hash() for item in changed_items
                    ],
                    vectors=[
                        self.embeddings_calculator.get_embeddings_from_item(item)
                        for item in changed_items
                    ],
                ),
            )
        else:
            print("no changed items to ingest")

    def create_collection(self, force=False):
        try:
            self.qdrant.get_collection(collection_name=self.collection_name)
            exists = True
        except:
            exists = False

        if not exists or force:
            self.qdrant.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.embeddings_calculator.vectors_size,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )

    def filter_to_qdrant_filter(self, filter):
        qdrant_filter = qdrant_models.Filter(
            must=[], must_not=[], should=[]
        )

        for key, value in filter.items():
            if key == "not":
                for key2, value2 in value.items():
                    qdrant_filter.must_not.append(
                        qdrant_models.FieldCondition(
                            key=key2,
                            match=qdrant_models.MatchValue(value=value2),
                        )
                    )
            else:
                qdrant_filter.must.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                )

        return qdrant_filter
