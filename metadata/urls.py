"""metadata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from patients import api_views


router = routers.DefaultRouter()
router.register(r'variants', api_views.VariantViewSet)
router.register(r'phenotypicfeatures', api_views.PhenotypicFeatureViewSet)
router.register(r'procedures', api_views.ProcedureViewSet)
router.register(r'htsfiles', api_views.HtsFileViewSet)
router.register(r'genes', api_views.GeneViewSet)
router.register(r'diseases', api_views.DiseaseViewSet)
router.register(r'resources', api_views.ResourceViewSet)
router.register(r'updates', api_views.UpdateViewSet)
router.register(r'externalreferences', api_views.ExternalReferenceViewSet)
router.register(r'metadata', api_views.MetaDataViewSet)
router.register(r'individuals', api_views.IndividualViewSet)
router.register(r'biosamples', api_views.BiosampleViewSet)
router.register(r'phenopackets', api_views.PhenopacketViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
