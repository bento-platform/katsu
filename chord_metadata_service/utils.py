from django.db.models import Model, QuerySet
from typing import Any, Set, Type

__all__ = [
    "build_id_set",
    "build_id_set_from_model",
]


async def build_id_set(qs: QuerySet, field: str) -> Set[Any]:
    s = set()
    async for v in qs.values_list(field, flat=True):
        s.add(v)
    return s


async def build_id_set_from_model(m: Type[Model], field: str) -> Set[Any]:
    return await build_id_set(m.objects.all(), field)
