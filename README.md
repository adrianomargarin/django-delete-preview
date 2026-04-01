# django-delete-preview

Preview cascade deletes before execution and enforce safe deletion with explicit confirmation.

## Features

- Inspect the full cascade delete tree for model instances and QuerySets
- Get a structured preview (JSON or human-readable text) **before** deleting
- Block accidental deletes on instances: `instance.delete()` raises unless you pass `confirm=True`
- For QuerySets, use `delete_with_preview(confirm=True)` — the standard `.delete()` on QuerySets is **not overridden**
- Django management command for inspecting from the command line
- Works with any Django model — no schema changes required
- Python 3.10+, Django 4.2+, fully typed

## Installation

```bash
pip install django-delete-preview
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_delete_preview",
]
```

## Quickstart

```python
from django_delete_preview.mixins import DeletePreviewMixin
from django_delete_preview.managers import DeletePreviewManager
from django.db import models


class Author(DeletePreviewMixin, models.Model):
    name = models.CharField(max_length=200)
    objects = DeletePreviewManager()


class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

## Usage

### Instance preview

```python
author = Author.objects.get(pk=1)
summary = author.preview_delete()
# {
#   "database": "default",
#   "total_objects": 3,
#   "models": {"myapp.Author": 1, "myapp.Book": 2},
#   "items": {"myapp.Author": ["Jane Austen"], "myapp.Book": ["Oliver Twist", "Great Expectations"]}
# }
```

### Safe instance delete

```python
# Without confirmation → raises ValueError
author.delete()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

# With confirmation → executes
author.delete(confirm=True)
```

### QuerySet preview

```python
summary = Author.objects.filter(active=False).preview_delete()
```

### QuerySet safe delete

Use `delete_with_preview()` — the standard Django `.delete()` is **not overridden** by this library,
so Django admin bulk actions and other internal framework usage continue to work normally.

```python
# Without confirmation → raises ValueError
Author.objects.filter(active=False).delete_with_preview()

# With confirmation → executes
Author.objects.filter(active=False).delete_with_preview(confirm=True)

# Standard .delete() still works normally (no protection)
Author.objects.filter(active=False).delete()
```

### Management command

```bash
# Preview (text output)
python manage.py preview_delete myapp.Author 1

# Preview (JSON output)
python manage.py preview_delete myapp.Author 1 --format json

# Preview + execute
python manage.py preview_delete myapp.Author 1 --execute
```

### JSON output format

```json
{
  "database": "default",
  "total_objects": 10,
  "models": {
    "myapp.Author": 1,
    "myapp.Order": 9
  }
}
```

## Configuration

```python
# settings.py — maximum number of item string representations per model (default: 100)
DELETE_PREVIEW_MAX_ITEMS = 50
```

## Limitations

- Does not support soft delete — objects are permanently deleted
- Does not preview `pre_delete` / `post_delete` signal side effects
- `fast_deletes` (objects deleted without loading into memory) are counted but may include approximate `str()` representations

## Example app

The repository includes a fully runnable Django project under `example/` that
demonstrates every feature of the library using a bookstore domain
(`Author`, `Book`, `Order`, `Publisher`).

### Setup

```bash
git clone https://github.com/adrianomargarin/django-delete-preview
cd django-delete-preview
pip install -e ".[dev]"

cd example
python manage.py migrate
python manage.py loaddata initial_data   # loads 3 authors, 9 books, 5 orders, 3 publishers
```

### Instance preview

```bash
python manage.py shell
```

```python
from bookstore.models import Author

author = Author.objects.get(pk=1)   # Jane Austen
author.preview_delete()
# {
#   "database": "default",
#   "total_objects": 6,
#   "models": {"bookstore.Author": 1, "bookstore.Book": 3, "bookstore.Order": 2},
#   "items": {
#     "bookstore.Author": ["Jane Austen"],
#     "bookstore.Book": ["Emma", "Persuasion", "Pride and Prejudice"],
#     "bookstore.Order": ["ORD-001", "ORD-002"]
#   }
# }
```

### Safe instance delete

```python
author.delete()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

author.delete(confirm=True)
# (6, {"bookstore.Book": 3, "bookstore.Order": 2, "bookstore.Author": 1})
```

### QuerySet preview

```python
from bookstore.models import Author

Author.objects.all().preview_delete()
# {
#   "database": "default",
#   "total_objects": 20,
#   "models": {"bookstore.Author": 3, "bookstore.Book": 9, "bookstore.Order": 5},
#   ...
# }
```

### QuerySet safe delete

```python
Author.objects.all().delete_with_preview()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

Author.objects.all().delete_with_preview(confirm=True)
# (20, {"bookstore.Book": 9, "bookstore.Order": 5, "bookstore.Author": 3})
```

### Management command

```bash
# Human-readable preview
python manage.py preview_delete bookstore.Author 1

# Database    : default
# Total items : 6
#
# Models affected:
#   bookstore.Author: 1
#   bookstore.Book: 3
#   bookstore.Order: 2
#
# Items:
#   bookstore.Author:
#     - Jane Austen
#   bookstore.Book:
#     - Emma
#     - Persuasion
#     - Pride and Prejudice
#   bookstore.Order:
#     - ORD-001
#     - ORD-002

# JSON preview
python manage.py preview_delete bookstore.Author 1 --format json

# Preview and execute
python manage.py preview_delete bookstore.Author 1 --execute
```

### Publisher (no cascade)

`Publisher` has no related models, so deleting one affects only itself:

```python
from bookstore.models import Publisher

pub = Publisher.objects.get(pk=1)
pub.preview_delete()
# {"database": "default", "total_objects": 1, "models": {"bookstore.Publisher": 1}, ...}

pub.delete(confirm=True)
```

## Development setup

```bash
git clone https://github.com/adrianomargarin/django-delete-preview
cd django-delete-preview
pip install -e ".[dev]"
pre-commit install

# Run tests
pytest

# Lint
ruff check src tests

# Type check
mypy src/django_delete_preview
```
