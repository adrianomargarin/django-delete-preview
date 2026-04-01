from __future__ import annotations

import pytest

from tests.models import Author, Book


@pytest.mark.django_db
class TestDeletePreviewQuerySet:
    def test_preview_delete_on_queryset(self) -> None:
        Author.objects.create(name="Author 1")
        Author.objects.create(name="Author 2")

        summary = Author.objects.all().preview_delete()

        assert summary["total_objects"] >= 2
        assert "tests.Author" in summary["models"]

    def test_preview_delete_with_cascade(self) -> None:
        author = Author.objects.create(name="With Books")
        Book.objects.create(title="Book A", author=author)
        Book.objects.create(title="Book B", author=author)

        summary = Author.objects.filter(pk=author.pk).preview_delete()

        assert summary["models"].get("tests.Author", 0) == 1
        assert summary["models"].get("tests.Book", 0) == 2

    def test_delete_with_preview_without_confirm_raises(self) -> None:
        Author.objects.create(name="To Delete")

        with pytest.raises(ValueError, match="Delete blocked"):
            Author.objects.all().delete_with_preview()

    def test_delete_with_preview_confirm_false_raises(self) -> None:
        Author.objects.create(name="To Delete 2")

        with pytest.raises(ValueError, match="Delete blocked"):
            Author.objects.all().delete_with_preview(confirm=False)

    def test_delete_with_preview_confirm_true_deletes(self) -> None:
        Author.objects.create(name="Author To Delete")
        Author.objects.create(name="Author To Delete 2")

        count, _ = Author.objects.all().delete_with_preview(confirm=True)

        assert count >= 2
        assert Author.objects.count() == 0

    def test_standard_delete_still_works(self) -> None:
        """Ensure .delete() is NOT overridden and works normally."""
        Author.objects.create(name="Plain Delete")

        count, _ = Author.objects.all().delete()

        assert count >= 1
        assert Author.objects.count() == 0

    def test_preview_max_items(self) -> None:
        author = Author.objects.create(name="Author Z")
        for i in range(20):
            Book.objects.create(title=f"Book {i}", author=author)

        summary = Author.objects.filter(pk=author.pk).preview_delete(max_items=5)

        for items in summary["items"].values():
            assert len(items) <= 5
