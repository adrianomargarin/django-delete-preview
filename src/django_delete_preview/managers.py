from __future__ import annotations

from django.db import models

from django_delete_preview.querysets import DeletePreviewQuerySet


class DeletePreviewManager(models.Manager["models.Model"]):
    """
    Custom manager that returns a DeletePreviewQuerySet.

    Usage::

        class Author(DeletePreviewMixin):
            objects = DeletePreviewManager()
    """

    def get_queryset(self) -> DeletePreviewQuerySet:
        """Return a DeletePreviewQuerySet for all model queries."""
        return DeletePreviewQuerySet(self.model, using=self._db)
