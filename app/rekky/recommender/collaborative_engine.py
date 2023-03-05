from pprint import pprint
from typing import List, Union
from rekky.recommender.types import Event, Item, RecommendedItem
from rekky.resources.elastic import get_elastic
from elasticsearch import helpers

from elasticsearch.exceptions import NotFoundError

from rekky.resources.qdrant import get_qdrant
from rekky.utils import uuid_or_int


class CollaborativeEngine(object):
    def __init__(self, collection_name: str):
        self.elastic = get_elastic()

        self.collection_name = collection_name
        self.create_collection()

    def get_items_from_ids(self, item_ids: List[Union[str, int]]):
        qdrant_items = get_qdrant().retrieve(
            collection_name=self.collection_name,
            ids=item_ids,
        )
        return [Item.from_qdrant_item(qdrant_item) for qdrant_item in qdrant_items]

    def get_items_seen_by_others(self, item_ids: List[str], offset=0, limit=10, minimum_interactions=2):
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "terms": {
                            "items": item_ids
                        }
                    }
                }
            },
            "aggregations": {
                "recommendations": {
                    "terms": {
                        "min_doc_count": minimum_interactions,
                        "field": "items",
                        "size": offset + limit,
                        "exclude": item_ids
                    }
                }
            },
            "size": 0
        }

        result = self.elastic.search(index=self.collection_name, body=body)

        pprint(result)

        buckets = result.get("aggregations").get("recommendations").get("buckets")
        if not buckets:
            return []

        counts_by_id = {bucket.get("key"): bucket.get("doc_count") for bucket in buckets}
        max_count = max(counts_by_id.values())

        paginated_buckets = buckets[offset: offset + limit]

        item_ids = list(map(lambda bucket: bucket.get("key"), paginated_buckets))
        items = self.get_items_from_ids(list(map(uuid_or_int, item_ids)))
        items_by_id = {item.id: item for item in items}

        recommended_items = []
        for item_id in item_ids:
            properties = {}
            if item_id in items_by_id:
                properties = items_by_id[item_id].properties

            score = counts_by_id[item_id] / max_count

            recommended_items.append(RecommendedItem(item=Item(id=item_id, properties=properties), score=score))

        return recommended_items

    def create_collection(self, force: bool = False):
        if force:
            self.elastic.indices.delete(self.collection_name)

        self.elastic.indices.create(index=self.collection_name, ignore=400, body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "dynamic": True,
                "dynamic_templates": [
                    {
                        "base": {
                            "match_mapping_type": "*",
                            "mapping": {
                                "type": "keyword"
                            }
                        }
                    }
                ],
                "properties": {
                    "user_id": {"type": "keyword"},
                    "event": {"type": "keyword"},
                    "items": {"type": "keyword"},
                }
            }
        })

    def construct_event_id(self, event: str, user_id: str):
        return "event-{}-{}-{}".format(
            self.collection_name,
            event,
            user_id
        )

    def get_user_by_id(self, user_document_id: str):
        try:
            return self.elastic.get(index=self.collection_name, id=user_document_id)
        except NotFoundError:
            return None

    def ingest(self, events: List[Event]):
        actions = []
        for event in events:
            document_id = self.construct_event_id(event.event, event.user_id)

            existing_interaction = self.get_user_by_id(document_id)

            if existing_interaction:
                existing_items = existing_interaction.get("_source", {}).get("items")
            else:
                existing_items = []

            new_items = [i for i in existing_items if i != event.item_id] + [event.item_id]

            actions.append({
                "_index": self.collection_name,
                "_id": document_id,
                "_source": {
                    "_date": event.date,
                    "user_id": event.user_id,
                    "event": event.event,
                    "items": new_items
                },
            })

        helpers.bulk(self.elastic, actions, refresh=True)
