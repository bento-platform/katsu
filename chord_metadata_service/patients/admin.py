from django.contrib import admin
from .models import *

# TODO: This should not be available outside of development mode.


@admin.register(Ontology)
class OntologyAdmin(admin.ModelAdmin):
    list_display = ("ontology_id", "label")


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    pass


@admin.register(PhenotypicFeature)
class PhenotypicFeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    pass


@admin.register(HtsFile)
class HtsFileAdmin(admin.ModelAdmin):
    pass


@admin.register(Gene)
class GeneAdmin(admin.ModelAdmin):
    pass


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(ExternalReference)
class ExternalReferenceAdmin(admin.ModelAdmin):
    pass


@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    pass


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    pass


@admin.register(Biosample)
class BiosampleAdmin(admin.ModelAdmin):
    pass


@admin.register(Phenopacket)
class PhenopacketAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(TableOwnership)
class TableOwnershipAdmin(admin.ModelAdmin):
    pass
