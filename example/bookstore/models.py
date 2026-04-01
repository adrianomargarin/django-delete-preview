"""
Bookstore models — mirrors the README Quickstart examples exactly.

Demonstrates:
- DeletePreviewMixin for safe instance delete + instance preview
- DeletePreviewManager for queryset preview + delete_with_preview

Cascade structure:
    Author ──< Book   (Book.author FK → Author, CASCADE)
    Author ──< Order  (Order.author FK → Author, CASCADE)
    Publisher         (standalone, no cascade in this example)
"""

from django.db import models

from django_delete_preview.managers import DeletePreviewManager
from django_delete_preview.mixins import DeletePreviewMixin


class Author(DeletePreviewMixin):
    """An author who wrote books and placed orders."""

    name = models.CharField(max_length=200)
    objects = DeletePreviewManager()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """A book written by an author."""

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Publisher(DeletePreviewMixin):
    """A publisher (standalone — demonstrates preview with no cascade)."""

    name = models.CharField(max_length=200)
    objects = DeletePreviewManager()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    """An order placed by a customer, associated with an author."""

    reference = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="orders")

    class Meta:
        ordering = ["reference"]

    def __str__(self) -> str:
        return self.reference
