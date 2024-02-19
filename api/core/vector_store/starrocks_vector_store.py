import copy
from typing import Any, Optional

from langchain.embeddings.base import Embeddings

from core.vector_store.vector.starrocks import StarRocks, StarRocksSettings, get_named_result


class StarRocksVectorStore(StarRocks):
    def __init__(
            self,
            embedding: Embeddings,
            config: Optional[StarRocksSettings] = None,
            index_name: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        cfg = copy.deepcopy(config)
        cfg.table = index_name
        super().__init__(embedding, cfg, **kwargs)

    def del_texts(self, where_filter: dict):
        if not where_filter or 'filter' not in where_filter:
            raise ValueError('where_filter must not be empty')

        get_named_result(
            self.connection,
            f'DELETE FROM {self.config.database}.{self.config} WHERE {where_filter["filter"]})'
        )

    def del_text(self, uuid: str) -> None:
        get_named_result(
            self.connection,
            f'DELETE FROM {self.config.database}.{self.config} WHERE id=\'{uuid}\''
        )

    def text_exists(self, uuid: str) -> bool:
        result = get_named_result(
            self.connection,
            f'SELECT COUNT(1) FROM {self.config.database}.{self.config} WHERE id=\'{uuid}\''
        )
        return result == 0

    def delete(self):
        self.drop()

    def get_ids_by_document_id(self, document_id: str):
        return self.get_ids_by_metadata_field('document_id', document_id)

    def get_ids_by_metadata_field(self, key: str, value: str):
        result = get_named_result(
            self.connection,
            f'SELECT id FROM {self.config.database}.{self.config} WHERE metadata->\'{key}\' = value'
        )
        if result:
            return [item["id"] for item in result]
        else:
            return None
