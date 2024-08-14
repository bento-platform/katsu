from django.db.models import Model, QuerySet
from collections import defaultdict
from typing import Any, Dict, List, Set, Type

__all__ = [
    "build_id_set",
    "build_id_set_from_model",
    "build_experiments_by_subject",
]


async def build_id_set(qs: QuerySet, field: str) -> Set[Any]:
    s = set()
    async for v in qs.values_list(field, flat=True):
        s.add(v)
    return s


async def build_id_set_from_model(m: Type[Model], field: str) -> Set[Any]:
    return await build_id_set(m.objects.all(), field)


def build_experiments_by_subject(biosamples_experiments_details: List[Dict]) -> Dict[str, List[Dict]]:
    experiments_with_biosamples = defaultdict(list)
    for b in biosamples_experiments_details:
        experiments_with_biosamples[b["subject_id"]].append({
            "biosample_id": b["biosample_id"],
            "sampled_tissue": {
                "id": b["tissue_id"],
                "label": b["tissue_label"]
            },
            "experiment": {
                "experiment_id": b["experiment_id"],
                "experiment_type": b["experiment_type"],
                "study_type": b["study_type"]
            }
        })
    return experiments_with_biosamples
