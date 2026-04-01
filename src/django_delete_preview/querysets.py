from __future__ import annotations

from django.db import models

from django_delete_preview.collector import DeleteSummary, get_delete_summary


class DeletePreviewQuerySet(models.QuerySet[models.Model]):
    """
    QuerySet subclass that adds delete-preview and safe-delete capabilities.

    Usage::

        authors = Author.objects.filter(active=False)

        # Preview what would be deleted
        summary = authors.preview_delete()

        # Safe delete (raises ValueError without confirm=True)
        authors.delete_with_preview(confirm=True)

        # Normal .delete() is NOT overridden and still works
        authors.delete()
    """

    def preview_delete(self, max_items: int | None = None) -> DeleteSummary:
        """
        Return a summary of all objects that would be deleted by this QuerySet.

        Args:
            max_items: Maximum number of item representations per model.

        Returns:
            DeleteSummary with database, total_objects, models, and items.
        """
        db = self.db
        return get_delete_summary(self, using=db, max_items=max_items)

    def delete_with_preview(
        self,
        confirm: bool = False,
    ) -> tuple[int, dict[str, int]]:
        """
        Delete the QuerySet objects, requiring explicit confirmation.

        Note: This does NOT override the standard .delete() method to avoid
        breaking Django admin bulk actions and other internal Django usage.

        Args:
            confirm: Must be True to execute the delete. If False, raises ValueError.

        Raises:
            ValueError: If confirm is not True.

        Returns:
            A (count, {model: count}) tuple, same as Django's QuerySet.delete().
        """
        if not confirm:
            raise ValueError(
                "Delete blocked. Run preview_delete() first and confirm the operation."
            )
        return self.delete()
