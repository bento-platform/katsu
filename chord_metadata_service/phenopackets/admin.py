from django.contrib import admin
from .models import *


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


# @admin.register(ExternalReference)
# class ExternalReferenceAdmin(admin.ModelAdmin):
#     pass


@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
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


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    pass


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass

@admin.register(Biosample)
class BiosampleAdmin(admin.ModelAdmin):
    pass


@admin.register(Phenopacket)
class PhenopacketAdmin(admin.ModelAdmin):
    pass


@admin.register(GenomicInterpretation)
class GenomicInterpretationAdmin(admin.ModelAdmin):
    pass


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    pass


@admin.register(Interpretation)
class InterpretationAdmin(admin.ModelAdmin):
    pass
