from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Document, Text, Date, Search, Object, Boolean
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models


connections.create_connection()

class IndividualIndex(Document):
    resourceType = Text()
    identifier = Text()
    birthDate = Date()
    gender = Text()
    active = Boolean()
    deceased = Boolean()

    class Meta:
        index = 'metadata'
