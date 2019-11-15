from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import (
	Document, Text, Date, Search,
	Object, Boolean, InnerDoc, Nested)
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch


connections.create_connection()


class OntologyIndex(InnerDoc):
	reference = Text()
	display = Text()

class Reference(InnerDoc):
	reference = Nested(OntologyIndex)


class BiosampleIndex(Document):
	resourceType = Text()
	identifier = Text()
	subject = Text()
	sex = Text()
	text = Text()
	parent = InnerDoc(
		properties={
		'reference': InnerDoc(
			properties={
				'reference': Text(),
				'display': Text()
			}
			)
		}
		)

	class Meta:
		index = 'metadata'
