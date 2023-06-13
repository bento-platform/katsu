from django.contrib import admin

from .models import Project, Dataset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass
