from dal import autocomplete
from .models import Disease, PhenotypicFeature, Biosample


class DiseaseTermAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 50

    def get_result_label(self, item):
        return item.term["label"]

    def get_selected_result_label(self, item):
        return item.term["label"]

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Disease.objects.none()

        qs = Disease.objects.all()
        if self.q:
            # looks for a matching string everywhere in term label field
            qs = qs.filter(term__label__icontains=self.q)

        return qs
