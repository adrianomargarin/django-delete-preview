from __future__ import annotations

import json

import pytest

from django_delete_preview.collector import DeleteSummary
from django_delete_preview.formatters import format_as_json, format_as_text


@pytest.fixture
def sample_summary() -> DeleteSummary:
    return DeleteSummary(
        database="default",
        total_objects=3,
        models={"myapp.Author": 1, "myapp.Book": 2},
        items={"myapp.Author": ["Jane Austen"], "myapp.Book": ["Book A", "Book B"]},
    )


class TestFormatAsText:
    def test_contains_database(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary)
        assert "default" in text

    def test_contains_total(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary)
        assert "3" in text

    def test_contains_model_labels(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary)
        assert "myapp.Author" in text
        assert "myapp.Book" in text

    def test_contains_items_when_enabled(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary, include_items=True)
        assert "Jane Austen" in text
        assert "Book A" in text

    def test_excludes_items_when_disabled(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary, include_items=False)
        assert "Jane Austen" not in text

    def test_structure(self, sample_summary: DeleteSummary) -> None:
        text = format_as_text(sample_summary)
        assert "Models affected:" in text


class TestFormatAsJson:
    def test_valid_json(self, sample_summary: DeleteSummary) -> None:
        output = format_as_json(sample_summary)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_json_contains_required_keys(self, sample_summary: DeleteSummary) -> None:
        data = json.loads(format_as_json(sample_summary))
        assert "database" in data
        assert "total_objects" in data
        assert "models" in data

    def test_json_excludes_items_by_default(
        self, sample_summary: DeleteSummary
    ) -> None:
        data = json.loads(format_as_json(sample_summary))
        assert "items" not in data

    def test_json_includes_items_when_requested(
        self, sample_summary: DeleteSummary
    ) -> None:
        data = json.loads(format_as_json(sample_summary, include_items=True))
        assert "items" in data
        assert "myapp.Author" in data["items"]

    def test_json_values_are_correct(self, sample_summary: DeleteSummary) -> None:
        data = json.loads(format_as_json(sample_summary))
        assert data["database"] == "default"
        assert data["total_objects"] == 3
        assert data["models"]["myapp.Author"] == 1
        assert data["models"]["myapp.Book"] == 2
