# coding: utf-8
from typing import cast, Any, List

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import VectorStore
from pydantic import BaseModel

from core.index.base import BaseIndex
from core.index.vector_index.base import BaseVectorIndex
from core.vector_store.starrocks_vector_store import StarRocksVectorStore
from core.vector_store.vector.starrocks import StarRocksSettings
from models.dataset import Dataset


class StarRocksConfig(BaseModel):
    endpoint: str = "localhost:9030"
    username: str = "root"
    password: str = ""
    database: str = "default"


class StarRocksVectorIndex(BaseVectorIndex):

    def __init__(self, dataset: Dataset, config: StarRocksConfig, embeddings: Embeddings, attributes: list):
        super().__init__(dataset, embeddings)
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

    def get_type(self) -> str:
        return 'starrocks'

    def get_index_name(self, dataset: Dataset) -> str:
        if self.dataset.index_struct_dict:
            class_prefix: str = self.dataset.index_struct_dict['vector_store']['class_prefix']
            if not class_prefix.endswith('_Node'):
                # original class_prefix
                class_prefix += '_Node'

            return class_prefix

        dataset_id = dataset.id
        return "Vector_index_" + dataset_id.replace("-", "_") + '_Node'

    def to_index_struct(self) -> dict:
        return {
            "type": self.get_type(),
            "vector_store": {"class_prefix": self.get_index_name(self.dataset)}
        }

    def create(self, texts: list[Document], **kwargs) -> BaseIndex:
        uuids = self._get_uuids(texts)
        self._vector_store = StarRocksVectorStore.from_documents(
            texts,
            self._embeddings,
            config=self._config,
            index_name=self.get_index_name(self.dataset),
            text_ids=uuids,
        )

        return self

    def create_with_collection_name(self, texts: list[Document], collection_name: str, **kwargs) -> BaseIndex:
        uuids = self._get_uuids(texts)
        self._vector_store = StarRocksVectorStore.from_documents(
            texts,
            self._embeddings,
            config=self._config,
            index_name=self.get_index_name(self.dataset),
            text_ids=uuids,
        )

        return self

    def _get_vector_store(self) -> VectorStore:
        """Only for created index."""
        if self._vector_store:
            return self._vector_store

        return StarRocksVectorStore(
            config=self._config,
            index_name=self.get_index_name(self.dataset),
            embedding=self._embeddings,
        )

    def _get_vector_store_class(self) -> type:
        return StarRocksVectorStore

    def delete_by_document_id(self, document_id: str):
        # if self._is_origin():
        #     self.recreate_dataset(self.dataset)
        #     return

        vector_store = self._get_vector_store()
        vector_store = cast(self._get_vector_store_class(), vector_store)
        ids = vector_store.get_ids_by_document_id(document_id)
        self.delete_by_ids_batch(ids)

    def delete_by_metadata_field(self, key: str, value: str):
        vector_store = self._get_vector_store()
        vector_store = cast(self._get_vector_store_class(), vector_store)
        ids = vector_store.get_ids_by_metadata_field(key, value)
        self.delete_by_ids_batch(ids)

    def delete_by_ids_batch(self, vector_store, ids):
        if ids:
            ids_cond = ','.join([f'\'{k}\'' for k in ids])
            vector_store.del_texts({
                'filter': f'id in ({ids_cond})'
            })

    def delete_by_group_id(self, group_id: str):
        if self._is_origin():
            self.recreate_dataset(self.dataset)
            return

        vector_store = self._get_vector_store()
        vector_store = cast(self._get_vector_store_class(), vector_store)

        vector_store.delete()

    # def _is_origin(self):
    #     if self.dataset.index_struct_dict:
    #         class_prefix: str = self.dataset.index_struct_dict['vector_store']['class_prefix']
    #         if not class_prefix.endswith('_Node'):
    #             # original class_prefix
    #             return True
    #
    #     return False

    def search_by_full_text_index(self, query: str, **kwargs: Any) -> List[Document]:
        vector_store = self._get_vector_store()
        vector_store = cast(self._get_vector_store_class(), vector_store)
        return vector_store.similarity_search_by_bm25(query, kwargs.get('top_k', 2), **kwargs)
