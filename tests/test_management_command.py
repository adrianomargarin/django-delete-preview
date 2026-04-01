from __future__ import annotations

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from tests.models import Author, PlainAuthor


@pytest.mark.django_db
class TestPreviewDeleteCommand:
    def test_text_output_single_object(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        author = Author.objects.create(name="Command Author")
        call_command("preview_delete", "tests.Author", str(author.pk))
        captured = capsys.readouterr()
        assert "tests.Author" in captured.out
        assert "1" in captured.out

    def test_text_output_with_cascade(
        self, author_with_books: Author, capsys: pytest.CaptureFixture[str]
    ) -> None:
        call_command("preview_delete", "tests.Author", str(author_with_books.pk))
        captured = capsys.readouterr()
        assert "tests.Book" in captured.out

    def test_json_output_is_parseable(
        self, author: Author, capsys: pytest.CaptureFixture[str]
    ) -> None:
        call_command(
            "preview_delete", "tests.Author", str(author.pk), "--format", "json"
        )
        captured = capsys.readouterr()
        # JSON output may be mixed with other lines; find the JSON object
        # The command outputs preview JSON then (if execute) result JSON
        # For preview-only, output should be a single JSON object
        data = json.loads(captured.out.strip())
        assert "total_objects" in data
        assert "models" in data

    def test_execute_deletes_object(self, author: Author) -> None:
        pk = author.pk
        call_command("preview_delete", "tests.Author", str(pk), "--execute")
        assert not Author.objects.filter(pk=pk).exists()

    def test_execute_with_json_format(
        self, author: Author, capsys: pytest.CaptureFixture[str]
    ) -> None:
        call_command(
            "preview_delete",
            "tests.Author",
            str(author.pk),
            "--format",
            "json",
            "--execute",
        )
        captured = capsys.readouterr()
        # With --execute and --format json, two JSON objects are concatenated.
        # Use a streaming decoder to parse both.
        decoder = json.JSONDecoder()
        text = captured.out.strip()
        idx = 0
        objects = []
        while idx < len(text):
            # Skip whitespace between objects
            while idx < len(text) and text[idx] in " \t\n\r":
                idx += 1
            if idx >= len(text):
                break
            obj, end = decoder.raw_decode(text, idx)
            objects.append(obj)
            idx = end
        assert len(objects) >= 1
        first = objects[0]
        assert "total_objects" in first

    def test_invalid_model_format_raises(self) -> None:
        with pytest.raises(CommandError, match="Invalid model format"):
            call_command("preview_delete", "InvalidModel", "1")

    def test_nonexistent_model_raises(self) -> None:
        with pytest.raises(CommandError, match="not found"):
            call_command("preview_delete", "tests.NonExistentModel", "1")

    def test_nonexistent_pk_raises(self, author: Author) -> None:
        with pytest.raises(CommandError, match="does not exist"):
            call_command("preview_delete", "tests.Author", "999999")

    def test_plain_model_without_mixin_works(self) -> None:
        """Management command works for models without DeletePreviewMixin."""
        plain = PlainAuthor.objects.create(name="Plain Author")
        pk = plain.pk
        call_command("preview_delete", "tests.PlainAuthor", str(pk), "--execute")
        assert not PlainAuthor.objects.filter(pk=pk).exists()
