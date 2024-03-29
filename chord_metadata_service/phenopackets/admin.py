from django.contrib import admin
from . import models as m


@admin.register(m.MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    pass


@admin.register(m.PhenotypicFeature)
class PhenotypicFeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Biosample)
class BiosampleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Phenopacket)
class PhenopacketAdmin(admin.ModelAdmin):
    pass


@admin.register(m.GenomicInterpretation)
class GenomicInterpretationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Interpretation)
class InterpretationAdmin(admin.ModelAdmin):
    pass
