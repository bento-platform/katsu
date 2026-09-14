from django.db.models import Q

__all__ = ["FACET_FIELDS", "active_facets", "apply_facets"]


# facet id -> (Dataset field name, is_array_field)
FACET_FIELDS: dict[str, tuple[str, bool]] = {
    "program": ("program_name", False),
    "project": ("project", False),
    "domain": ("domain", True),
    "taxon": ("taxa_labels", True),
    "access": ("privacy", False),
    "license": ("license_label", False),
    "context": ("study_context", False),
    "status": ("study_status", False),
    "keyword": ("keyword_labels", True),
}


def active_facets(query_params) -> dict[str, list[str]]:
    """Facet id -> selected values, for every facet with at least one value present in the request."""
    active = {}
    for facet_id in FACET_FIELDS:
        values = query_params.getlist(facet_id)
        if values:
            active[facet_id] = values
    return active


def apply_facets(qs, active: dict[str, list[str]], skip: str | None = None):
    """Apply every active facet filter except `skip` (AND across facets, OR within a facet)."""
    for facet_id, values in active.items():
        if facet_id == skip:
            continue
        field_name, is_array = FACET_FIELDS[facet_id]
        if is_array:
            q = Q()
            for v in values:
                q |= Q(**{f"{field_name}__overlap": [v]})
            qs = qs.filter(q)
        else:
            qs = qs.filter(**{f"{field_name}__in": values})
    return qs
