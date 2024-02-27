import copy
from typing import Any, Optional

from core.rag.datasource.vdb.starrock.client.starrocks import StarRocks, StarRocksSettings, get_named_result


class EnhancedStarRocks(StarRocks):
    def __init__(
            self,
            config: Optional[StarRocksSettings] = None,
            index_name: Optional[str] = None,
            auto_create_schema: bool = False,
            **kwargs: Any,
    ) -> None:
        cfg = copy.deepcopy(config)
        cfg.table = index_name
        super().__init__(cfg, auto_create_schema, **kwargs)

    def del_text_with_filter(self, where_filter: dict):
        if not where_filter or 'filter' not in where_filter:
            raise ValueError('where_filter must not be empty')

        get_named_result(
            self.connection,
            f'DELETE FROM {self.config.database}.{self.config} WHERE {where_filter["filter"]})'
        )

    def del_text_batch(self, uuids: list[str]):
        ids_cond = ','.join([f'\'{k}\'' for k in uuids])
        self.del_text_with_filter({
            'filter': f'id in ({ids_cond})'
        })

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
