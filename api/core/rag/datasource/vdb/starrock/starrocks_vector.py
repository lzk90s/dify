from typing import Any

from langchain.schema import Document
from pydantic import BaseModel

from core.rag.datasource.vdb.starrock.client.enhanced_starrocks import EnhancedStarRocks
from core.rag.datasource.vdb.starrock.client.starrocks import StarRocksSettings
from core.rag.datasource.vdb.vector_base import BaseVector
from models.dataset import Dataset


class StarRocksConfig(BaseModel):
    endpoint: str = "localhost:9030"
    username: str = "root"
    password: str = ""
    database: str = "default"


class StarRocksVector(BaseVector):

    def __init__(self, collection_name: str, config: StarRocksConfig):
        super().__init__(collection_name)
        addr = config.endpoint.split(':')
        if not addr or len(addr) != 2:
            raise ValueError('Invalid endpoint')
        self._config = StarRocksSettings(
            host=addr[0],
            port=addr[1],
            username=config.username,
            password=config.password,
            database=config.database,
        )
        self.client = self._init_client(config)

    def _init_client(self, collection_name) -> EnhancedStarRocks:
        return EnhancedStarRocks(self._config, collection_name, auto_create_schema=False)

    def get_type(self) -> str:
        return 'starrocks'

    def get_collection_name(self, dataset: Dataset) -> str:
        if dataset.index_struct_dict:
            class_prefix: str = dataset.index_struct_dict['vector_store']['class_prefix']
            if not class_prefix.endswith('_Node'):
                # original class_prefix
                class_prefix += '_Node'

            return class_prefix

        dataset_id = dataset.id
        return "Vector_index_" + dataset_id.replace("-", "_") + '_Node'

    def to_index_struct(self) -> dict:
        return {
            "type": self.get_type(),
            "vector_store": {"class_prefix": self._collection_name}
        }

    def create(self, texts: list[Document], embeddings: list[list[float]], **kwargs):
        self.add_texts(texts, embeddings)

    def add_texts(self, documents: list[Document], embeddings: list[list[float]], **kwargs):
        uuids = self._get_uuids(documents)
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]
        self.client.add_texts(texts, embeddings, metadatas, ids=uuids)

    def text_exists(self, id: str) -> bool:
        return self.client.text_exists(id)

    def delete_by_ids(self, ids: list[str]) -> None:
        self.client.del_text_batch(ids)

    def delete_by_metadata_field(self, key: str, value: str) -> None:
        ids = self.client.get_ids_by_metadata_field(key, value)
        self.client.del_text_batch(ids)

    def search_by_vector(
            self,
            query_vector: list[float],
            **kwargs: Any
    ) -> list[Document]:
        return self.client.similarity_search_by_vector(query_vector, **kwargs)

    def search_by_full_text(
            self, query: str,
            **kwargs: Any
    ) -> list[Document]:
        raise NotImplementedError()

    def delete(self) -> None:
        raise self.client.delete()
