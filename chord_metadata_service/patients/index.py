from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Document, Text, Date, Search, Object, Boolean
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models


connections.create_connection()

class IndividualIndex(Document):
	individual_id = Text()
	alternate_ids = Object()
	date_of_birth = Date()
	age = Text()
	sex = Text()
	karyotypic_sex = Text()
	taxonomy = Object()
	active = Boolean()
	deceased = Boolean()

	class Meta:
		index = 'metadata'
