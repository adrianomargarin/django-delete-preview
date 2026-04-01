from __future__ import annotations

import pytest

from tests.models import Author, Book


@pytest.mark.django_db
class TestDeletePreviewMixin:
    def test_preview_delete_returns_summary(self, author: Author) -> None:
        summary = author.preview_delete()

        assert "database" in summary
        assert "total_objects" in summary
        assert "models" in summary
        assert "items" in summary
        assert summary["total_objects"] >= 1

    def test_preview_delete_includes_cascade(self, author_with_books: Author) -> None:
        summary = author_with_books.preview_delete()

        assert summary["total_objects"] >= 3
        assert summary["models"].get("tests.Author", 0) == 1
        assert summary["models"].get("tests.Book", 0) == 2

    def test_delete_without_confirm_raises_value_error(self, author: Author) -> None:
        with pytest.raises(ValueError, match="Delete blocked"):
            author.delete()

    def test_delete_with_confirm_false_raises_value_error(self, author: Author) -> None:
        with pytest.raises(ValueError, match="Delete blocked"):
            author.delete(confirm=False)

    def test_delete_with_confirm_true_succeeds(self, author: Author) -> None:
        pk = author.pk
        count, _by_model = author.delete(confirm=True)

        assert count >= 1
        assert not Author.objects.filter(pk=pk).exists()

    def test_delete_with_confirm_true_deletes_cascade(
        self, author_with_books: Author
    ) -> None:
        author_pk = author_with_books.pk
        book_pks = list(
            Book.objects.filter(author=author_with_books).values_list("pk", flat=True)
        )

        author_with_books.delete(confirm=True)

        assert not Author.objects.filter(pk=author_pk).exists()
        for pk in book_pks:
            assert not Book.objects.filter(pk=pk).exists()

    def test_preview_delete_uses_specified_using(self, author: Author) -> None:
        summary = author.preview_delete(using="default")
        assert summary["database"] == "default"
