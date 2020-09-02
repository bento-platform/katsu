import graphene

import chord_metadata_service.patients.schema


class Query(chord_metadata_service.patients.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
