from __future__ import annotations

from typing import Any

from django.db import models, router

from django_delete_preview.collector import DeleteSummary, get_delete_summary


class DeletePreviewMixin(models.Model):
    """
    Abstract mixin that adds delete-preview and safe-delete capabilities to a model.

    Usage::

        class Author(DeletePreviewMixin):
            name = models.CharField(max_length=200)

        # Preview what would be deleted
        summary = author.preview_delete()

        # Safe delete (raises ValueError without confirm=True)
        author.delete(confirm=True)
    """

    class Meta:
        abstract = True

    def preview_delete(
        self,
        using: str | None = None,
        max_items: int | None = None,
    ) -> DeleteSummary:
        """
        Return a summary of all objects that would be deleted.

        Args:
            using: Database alias. Defaults to the instance's database.
            max_items: Maximum number of item representations per model.

        Returns:
            DeleteSummary with database, total_objects, models, and items.
        """
        db = (
            using
            or self._state.db
            or router.db_for_write(self.__class__, instance=self)
        )
        return get_delete_summary([self], using=db, max_items=max_items)

    def delete(  # type: ignore[override]
        self,
        using: Any = None,
        keep_parents: bool = False,
        confirm: bool = False,
    ) -> tuple[int, dict[str, int]]:
        """
        Delete this object, requiring explicit confirmation.

        Args:
            using: Database alias.
            keep_parents: If True, keep parent model instances for
                multi-table inheritance.
            confirm: Must be True to execute the delete. If False, raises ValueError.

        Raises:
            ValueError: If confirm is not True.

        Returns:
            A (count, {model: count}) tuple, same as Django's Model.delete().
        """
        if not confirm:
            raise ValueError(
                "Delete blocked. Run preview_delete() first and confirm the operation."
            )
        return super().delete(using=using, keep_parents=keep_parents)  # type: ignore[return-value]
