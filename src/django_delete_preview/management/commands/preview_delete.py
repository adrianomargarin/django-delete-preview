from __future__ import annotations

import json
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.db.models.deletion import Collector

from django_delete_preview.collector import get_delete_summary
from django_delete_preview.formatters import format_as_json, format_as_text


class Command(BaseCommand):
    """
    Preview (and optionally execute) the cascade delete for a single model instance.

    Usage::

        python manage.py preview_delete app_label.ModelName pk
        python manage.py preview_delete app_label.ModelName pk --format json
        python manage.py preview_delete app_label.ModelName pk --execute
    """

    help = "Preview cascade deletes for a model instance before executing."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "model",
            type=str,
            help="Model in 'app_label.ModelName' format (e.g. myapp.Author).",
        )
        parser.add_argument(
            "pk",
            type=str,
            help="Primary key of the object to inspect.",
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            default=False,
            help="Execute the delete after previewing.",
        )
        parser.add_argument(
            "--format",
            dest="output_format",
            choices=["text", "json"],
            default="text",
            help="Output format: 'text' (default) or 'json'.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Database alias to use (default: 'default').",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        model_path: str = options["model"]
        pk: str = options["pk"]
        execute: bool = options["execute"]
        output_format: str = options["output_format"]
        database: str = options["database"]

        # Resolve model class
        try:
            app_label, model_name = model_path.split(".", 1)
        except ValueError:
            raise CommandError(
                f"Invalid model format '{model_path}'. Use 'app_label.ModelName'."
            ) from None

        try:
            model_class = apps.get_model(app_label, model_name)
        except LookupError:
            raise CommandError(f"Model '{model_path}' not found.") from None

        # Fetch the object
        try:
            obj = model_class._default_manager.using(database).get(pk=pk)
        except model_class.DoesNotExist:
            raise CommandError(
                f"{model_path} with pk={pk!r} does not exist in database '{database}'."
            ) from None

        # Build preview
        summary = get_delete_summary([obj], using=database)

        # Output
        if output_format == "json":
            self.stdout.write(format_as_json(summary, include_items=False))
        else:
            self.stdout.write(format_as_text(summary, include_items=True))

        # Execute if requested
        if execute:
            if output_format != "json":
                self.stdout.write("\nExecuting delete...")

            # Use Collector directly so this works regardless of mixin usage
            collector = Collector(using=database)
            collector.collect([obj])
            deleted_count, deleted_by_model = collector.delete()

            if output_format == "json":
                self.stdout.write(
                    json.dumps(
                        {"deleted": deleted_count, "by_model": deleted_by_model},
                        indent=2,
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {deleted_count} object(s) across "
                        f"{len(deleted_by_model)} model(s)."
                    )
                )
