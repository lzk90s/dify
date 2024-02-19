import logging
import re

import jieba
from flask_restful import Resource, reqparse
from scipy import spatial

from vendor.extdata import api
from vendor.extdata.const import EMBEDDING_TEMPLATES
from vendor.extdata.dev import DeviceFactory

log = logging.getLogger(__name__)


def strings_ranked_by_relatedness(
        query_embedding: list,
        df: list[dict],
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 4,
        min_relatedness: float = 0.8
) -> tuple[list[str], list[float]] or None:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    strings_and_relatednesses = [
        (row["type"], row['desc'], relatedness_fn(query_embedding, row["embedding"])) for row in df
    ]
    strings_and_relatednesses = [s for s in strings_and_relatednesses if s[2] >= min_relatedness]
    if not strings_and_relatednesses:
        return None, None, None

    strings_and_relatednesses.sort(key=lambda x: x[2], reverse=True)
    types, descs, relatednesses = zip(*strings_and_relatednesses)
    return types[:top_n], descs[:top_n], relatednesses[:top_n]


def contains_alphanumeric(string):
    pattern = r'^[a-zA-Z0-9]+$'
    return True if re.search(pattern, string) else False


class DiagnoseToolApi(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('point', type=str, required=True, location='json')
        parser.add_argument('params', type=dict, location='json')
        args = parser.parse_args()
        point = args['point']
        if point == "ping":
            return {
                "result": "pong"
            }
        elif point == "app.external_data_tool.query":
            return self.handle_app_external_data_tool_query(params=args['params'])
        else:
            raise Exception("Not implemented")

    def handle_app_external_data_tool_query(self, params: dict):
        app_id = params.get("app_id")
        tool_variable = params.get("tool_variable")
        inputs = params.get("inputs")
        query = params.get("query")
        query_embedding = params.get('query_embedding')

        # for debug
        log.info(f"app_id: {app_id}, tool_variable: {tool_variable}, inputs: {inputs}, query: {query}")

        dev_id = inputs.get("dev_id") if 'dev_id' in inputs else None
        if not dev_id:
            dev_id = self.parse_dev_id_from_query(query)
            log.info(f'parsed dev {dev_id} from query {query}')
            if not dev_id:
                dev_id = 'mock'

        if not dev_id:
            return {
                "result": ''
            }

        dev = DeviceFactory.find_dev_by_id(dev_id)

        if not dev:
            result = "设备不存在，请检查设备是否有效"
        elif query_embedding:
            result = dev.__str__()
            topn_types, topn_descs, topn_sims = strings_ranked_by_relatedness(query_embedding,
                                                                              df=EMBEDDING_TEMPLATES,
                                                                              top_n=1)
            if topn_types:
                biz = topn_types[0]
                sim = topn_sims[0]
                log.info(f'biz={biz}, sim={sim}')
                biz_reason = dev.diagnose(biz)
                if biz_reason:
                    result += f'\n{topn_descs[0]}原因: {biz_reason}'
        else:
            result = ""

        log.info(f'result: {result}')
        return {
            "result": result
        }

    @classmethod
    def parse_dev_id_from_query(cls, query):
        seg_list = jieba.cut(query, cut_all=False)
        sl = [t for t in seg_list]
        dev_id = None
        for i, x in enumerate(sl):
            if contains_alphanumeric(x) and len(x) > 4:
                for j in range(i, i - 4, -1):
                    if j < 0:
                        break
                    k = sl[j]
                    if '设备' in k or 'dev' in k:
                        dev_id = x
        return dev_id


api.add_resource(DiagnoseToolApi, '/diagnose')
