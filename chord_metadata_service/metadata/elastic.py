import logging
from elasticsearch import Elasticsearch
from .settings import ELASTICSEARCH


logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

if ELASTICSEARCH:
    es = Elasticsearch()
    if not es.ping():
        raise ValueError("Connection to Elasticsearch failed")
else:
    es = None
