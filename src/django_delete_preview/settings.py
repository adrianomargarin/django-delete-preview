from django.conf import settings


def get_max_items() -> int:
    """Return the configured maximum number of preview items."""
    return int(getattr(settings, "DELETE_PREVIEW_MAX_ITEMS", 100))
