from django.db.models import Model
from typing import Set, Type, Union

from ..logger import logger
from ..utils import build_id_set

__all__ = [
    "remove_items",
    "remove_not_referenced",
]


async def remove_items(model: Type[Model], to_remove: Set[Union[int, str, None]], name_plural: str) -> int:
    n_to_remove = len(to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} {name_plural}: {str(to_remove)}")
        await model.objects.filter(id__in=to_remove).adelete()
    else:
        logger.info(f"No {name_plural} set for auto-removal")

    return n_to_remove


async def remove_not_referenced(model: Type[Model], references: Set[Union[int, str, None]], name_plural: str) -> int:
    objs_referenced = references.copy()

    # Remove null from set
    objs_referenced.discard(None)

    # Remove objects NOT in reference set
    objs_to_remove = await build_id_set(model.objects.exclude(id__in=objs_referenced), "id")
    return await remove_items(model, objs_to_remove, name_plural)
