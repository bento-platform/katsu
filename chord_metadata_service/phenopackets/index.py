from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import (
	Document, Text, Date, Search,
	Object, Boolean, InnerDoc, Nested)
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch


connections.create_connection()


class Ontology(InnerDoc):
	reference = Text()
	display = Text()

class Reference(InnerDoc):
	reference = Object(Ontology)
	comment = Text()

class SubjectReference(InnerDoc):
	reference = Text()

class BiosampleIndex(Document):
	resourceType = Text()
	identifier = Text()
	subject = Object(SubjectReference)
	sex = Text()
	text = Text()
	parent = Object(Reference)

	class Meta:
		index = 'metadata'


class Coding(InnerDoc):
	system = Text()
	code = Text()
	display = Text()


class Code(InnerDoc):
	coding = Object(Coding)


class ProcedureIndex(Document):
	resourceType = Text()
	identifier = Text()
	code = Object(Code)
	bodySite = Object(Code)

	class Meta:
		index = 'metadata'

class Extension(InnerDoc):
	code = Object(Code)

class PhenotypicFeatureDocument(Document):
	resourceType = Text()
	identifier = Text()
	note = Text()
	code = Object(Code)
	specimen = Object(SubjectReference)
	interpretation = Object(Code)
	phenotypic_feature_severity = Object(Extension)
	phenotypic_feature_modifier = Object(Extension)
	phenotypic_feature_onset = Object(Extension)
	evidence = Object(Extension)

	class Meta:
		index = 'metadata'
		