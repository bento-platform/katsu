from django.contrib import admin
from .models import *


@admin.register(GeneticVariantTested)
class GeneticVariantTestedAdmin(admin.ModelAdmin):
    pass


@admin.register(GeneticVariantFound)
class GeneticVariantFoundAdmin(admin.ModelAdmin):
    pass


@admin.register(GenomicsReport)
class GenomicsReportAdmin(admin.ModelAdmin):
    pass


@admin.register(LabsVital)
class LabsVitalAdmin(admin.ModelAdmin):
    pass


@admin.register(CancerCondition)
class CancerConditionAdmin(admin.ModelAdmin):
    pass


@admin.register(TNMStaging)
class TNMStagingAdmin(admin.ModelAdmin):
    pass


@admin.register(CancerRelatedProcedure)
class CancerRelatedProcedureAdmin(admin.ModelAdmin):
    pass


@admin.register(MedicationStatement)
class MedicationStatementAdmin(admin.ModelAdmin):
    pass


