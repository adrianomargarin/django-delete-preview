from __future__ import annotations

import pytest

from django_delete_preview.collector import get_delete_summary
from tests.models import Author, Book


@pytest.mark.django_db
class TestGetDeleteSummary:
    def test_single_object_no_cascade(self) -> None:
        author = Author.objects.create(name="Solo Author")
        summary = get_delete_summary([author], using="default")

        assert summary["database"] == "default"
        assert summary["total_objects"] >= 1
        assert "tests.Author" in summary["models"]
        assert summary["models"]["tests.Author"] == 1

    def test_cascade_counts_related_objects(self) -> None:
        author = Author.objects.create(name="Prolific Author")
        Book.objects.create(title="Book One", author=author)
        Book.objects.create(title="Book Two", author=author)

        summary = get_delete_summary([author], using="default")

        assert summary["total_objects"] >= 3
        assert summary["models"].get("tests.Author", 0) == 1
        assert summary["models"].get("tests.Book", 0) == 2

    def test_max_items_caps_item_list(self) -> None:
        author = Author.objects.create(name="Author X")
        for i in range(10):
            Book.objects.create(title=f"Book {i}", author=author)

        summary = get_delete_summary([author], using="default", max_items=3)

        book_items = summary["items"].get("tests.Book", [])
        assert len(book_items) <= 3

    def test_queryset_input(self) -> None:
        Author.objects.create(name="Author A")
        Author.objects.create(name="Author B")

        qs = Author.objects.all()
        summary = get_delete_summary(qs, using="default")

        assert summary["total_objects"] >= 2

    def test_items_contain_string_representations(self) -> None:
        author = Author.objects.create(name="String Author")
        summary = get_delete_summary([author], using="default")

        author_items = summary["items"].get("tests.Author", [])
        assert any("String Author" in item for item in author_items)
