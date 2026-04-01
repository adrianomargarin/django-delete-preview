from django.db import models

from django_delete_preview.managers import DeletePreviewManager
from django_delete_preview.mixins import DeletePreviewMixin


class Author(DeletePreviewMixin):
    """Author model using both the mixin and custom manager."""

    name = models.CharField(max_length=200)
    objects = DeletePreviewManager()

    class Meta:
        app_label = "tests"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """Book with a CASCADE FK to Author — used to test cascade previews."""

    title = models.CharField(max_length=300)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")

    class Meta:
        app_label = "tests"

    def __str__(self) -> str:
        return self.title


class Publisher(DeletePreviewMixin):
    """Publisher model using only the mixin (no custom manager)."""

    name = models.CharField(max_length=200)

    class Meta:
        app_label = "tests"

    def __str__(self) -> str:
        return self.name


class ProtectedBook(models.Model):
    """Book with a PROTECT FK to Publisher — delete should raise ProtectedError."""

    title = models.CharField(max_length=300)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.PROTECT, related_name="protected_books"
    )

    class Meta:
        app_label = "tests"

    def __str__(self) -> str:
        return self.title


class PlainAuthor(models.Model):
    """Author without any mixin — used in management command tests."""

    name = models.CharField(max_length=200)

    class Meta:
        app_label = "tests"

    def __str__(self) -> str:
        return self.name
