"""App configuration for the bookstore example app."""

from django.apps import AppConfig


class BookstoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookstore"
    verbose_name = "Bookstore"
