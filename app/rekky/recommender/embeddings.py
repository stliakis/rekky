import os
from typing import Union
from openai.embeddings_utils import (
    get_embedding
)

from rekky.recommender.types import Item
from rekky.settings import get_settings
from rekky.utils import listify


class EmbeddingsCalculator(object):
    vectors_size = None


class OpenAiEmbeddingsCalculator(EmbeddingsCalculator):
    def __init__(self, model=None):
        os.environ["OPENAI_API_KEY"] = get_settings().OPENAI_API_KEY
        self.model = model or get_settings().OPENAI_EMBEDDINGS_MODEL
        self.vectors_size = 1536

    def item_to_string(self, item: Item):
        return self.properties_to_string(item.properties)

    def properties_to_string(self, properties):
        return ", ".join([
            f"{key}={' '.join(map(str, listify(value)))}" for key, value in properties.items()
        ])

    def get_embeddings_from_item(self, item: Item):
        string = self.item_to_string(item)
        vector = get_embedding(string, self.model)
        return vector

    def get_embeddings_from_properties(self, properties: dict[str, Union[str, int, float, bool]]):
        string = self.properties_to_string(properties)
        vector = get_embedding(string, self.model)
        return vector
