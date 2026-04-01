"""
django-delete-preview
~~~~~~~~~~~~~~~~~~~~~
Preview cascade deletes before execution and enforce safe deletion
with explicit confirmation.
"""

__version__ = "0.1.1"
default_app_config = "django_delete_preview.apps.DeletePreviewConfig"

__all__ = [
    "DeletePreviewConfig",
    "DeletePreviewManager",
    "DeletePreviewMixin",
    "DeletePreviewQuerySet",
    "DeleteSummary",
    "__version__",
    "get_delete_summary",
]


def __getattr__(name: str) -> object:
    if name == "DeletePreviewConfig":
        from django_delete_preview.apps import DeletePreviewConfig

        return DeletePreviewConfig
    if name == "DeleteSummary":
        from django_delete_preview.collector import DeleteSummary

        return DeleteSummary
    if name == "get_delete_summary":
        from django_delete_preview.collector import get_delete_summary

        return get_delete_summary
    if name == "DeletePreviewManager":
        from django_delete_preview.managers import DeletePreviewManager

        return DeletePreviewManager
    if name == "DeletePreviewMixin":
        from django_delete_preview.mixins import DeletePreviewMixin

        return DeletePreviewMixin
    if name == "DeletePreviewQuerySet":
        from django_delete_preview.querysets import DeletePreviewQuerySet

        return DeletePreviewQuerySet
    raise AttributeError(f"module 'django_delete_preview' has no attribute {name!r}")
