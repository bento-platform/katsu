from dal import autocomplete
from .models import Disease, PhenotypicFeature, Biosample


class DiseaseTermAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 50

    # get_result_value return result.pk

    def get_result_label(self, item):
        return item.term["label"]

    def get_selected_result_label(self, item):
        return item.term["label"]

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Disease.objects.none()

        qs = Disease.objects.all().order_by("term__label")
        if self.q:
            # looks for a matching string everywhere in term label field
            qs = qs.filter(term__label__icontains=self.q)

        return qs


class PhenotypicFeatureTypeAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 50

    def get_result_value(self, result):
        # returns phenotypic feature type ontology id
        return str(result.pftype["id"])

    def get_result_label(self, item):
        return item.pftype["label"]

    def get_queryset(self):
        qs = PhenotypicFeature.objects.all().distinct("pftype__label").order_by("pftype__label")
        if self.q:
            # looks for a matching string everywhere in pf type label field
            qs = qs.filter(pftype__label__icontains=self.q)

        return qs


class BiosampleSampledTissueAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 50

    def get_result_value(self, result):
        # returns biosample sample tissue ontology id
        return str(result.sampled_tissue["id"])

    def get_result_label(self, item):
        return item.sampled_tissue["label"]

    def get_queryset(self):
        qs = Biosample.objects.all().distinct("sampled_tissue__label").order_by("sampled_tissue__label")
        if self.q:
            # looks for a matching string everywhere in sampled_tissue label field
            qs = qs.filter(sampled_tissue__label__icontains=self.q)

        return qs
