from __future__ import annotations

import pytest

from tests.models import Author, Book


@pytest.fixture
def author(db: None) -> Author:
    """A single Author instance with no related books."""
    return Author.objects.create(name="Jane Austen")


@pytest.fixture
def author_with_books(db: None) -> Author:
    """An Author instance with two related Books (cascade delete scenario)."""
    a = Author.objects.create(name="Charles Dickens")
    Book.objects.create(title="Oliver Twist", author=a)
    Book.objects.create(title="Great Expectations", author=a)
    return a
