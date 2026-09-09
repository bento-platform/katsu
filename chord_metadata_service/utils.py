from typing import Any

from django.db.models import Model, QuerySet

__all__ = [
    "build_id_set",
    "build_id_set_from_model",
]


async def build_id_set(qs: QuerySet, field: str) -> set[Any]:
    s = set()
    async for v in qs.values_list(field, flat=True):
        s.add(v)
    return s


async def build_id_set_from_model(m: type[Model], field: str) -> set[Any]:
    return await build_id_set(m.objects.all(), field)
