# coding: utf-8
from flask import Blueprint

from libs.external_api import ExternalApi

bp = Blueprint('tools', __name__, url_prefix='/tools/api')
api = ExternalApi(bp)

from vendor.extdata import diagnose_tool
