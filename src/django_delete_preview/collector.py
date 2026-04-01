from __future__ import annotations

from typing import Any

from django.db import models
from django.db.models.deletion import Collector
from django.db.models.query import QuerySet

from django_delete_preview.settings import get_max_items


class DeleteSummary(dict):  # type: ignore[type-arg]
    """Typed dict-like container for delete preview results."""

    database: str
    total_objects: int
    models: dict[str, int]
    items: dict[str, list[str]]


def get_delete_summary(
    objs: list[Any] | QuerySet[Any],
    using: str,
    max_items: int | None = None,
) -> DeleteSummary:
    """
    Collect cascade delete information without performing the actual delete.

    Args:
        objs: A list of model instances or a QuerySet to inspect.
        using: The database alias to use.
        max_items: Maximum number of item string representations to include per model.
                   Defaults to DELETE_PREVIEW_MAX_ITEMS setting.

    Returns:
        A DeleteSummary dict with keys: database, total_objects, models, items.
    """
    if max_items is None:
        max_items = get_max_items()

    collector = Collector(using=using)

    if isinstance(objs, QuerySet):
        collector.collect(objs)
    else:
        collector.collect(objs)

    model_counts: dict[str, int] = {}
    model_items: dict[str, list[str]] = {}

    # Process collector.data (objects loaded into memory)
    for model, instances in collector.data.items():
        label = _model_label(model)
        count = len(instances)
        model_counts[label] = model_counts.get(label, 0) + count
        existing = model_items.get(label, [])
        for obj in list(instances)[: max(0, max_items - len(existing))]:
            existing.append(str(obj))
        model_items[label] = existing

    # Process collector.fast_deletes (QuerySets deleted without loading into memory)
    for qs in collector.fast_deletes:
        if not isinstance(qs, QuerySet):
            continue
        model = qs.model
        label = _model_label(model)
        count = qs.count()
        model_counts[label] = model_counts.get(label, 0) + count
        existing = model_items.get(label, [])
        slots = max(0, max_items - len(existing))
        if slots > 0:
            for obj in qs[:slots]:
                existing.append(str(obj))
        model_items[label] = existing

    total = sum(model_counts.values())

    summary = DeleteSummary(
        database=using,
        total_objects=total,
        models=model_counts,
        items=model_items,
    )
    return summary


def _model_label(model: type[models.Model]) -> str:
    """Return 'app_label.ModelName' for a model class."""
    return f"{model._meta.app_label}.{model.__name__}"
