# django-delete-preview

Visualize exclusões em cascata antes de executá-las e imponha exclusão segura com confirmação explícita.

## Funcionalidades

- Inspecione a árvore completa de exclusão em cascata para instâncias e QuerySets
- Obtenha uma prévia estruturada (JSON ou texto legível) **antes** de excluir
- Bloqueie exclusões acidentais em instâncias: `instance.delete()` lança exceção a menos que `confirm=True` seja passado
- Para QuerySets, use `delete_with_preview(confirm=True)` — o `.delete()` padrão do QuerySet **não é sobrescrito**
- Comando de gerenciamento Django para inspeção via linha de comando
- Funciona com qualquer modelo Django — sem alterações no esquema
- Python 3.10+, Django 4.2+, totalmente tipado

## Instalação

```bash
pip install django-delete-preview
```

Adicione ao `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_delete_preview",
]
```

## Início rápido

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

## Uso

### Prévia de instância

```python
author = Author.objects.get(pk=1)
summary = author.preview_delete()
# {
#   "database": "default",
#   "total_objects": 3,
#   "models": {"myapp.Author": 1, "myapp.Book": 2},
#   "items": {"myapp.Author": ["Jane Austen"], "myapp.Book": ["Oliver Twist", "Grandes Esperanças"]}
# }
```

### Exclusão segura de instância

```python
# Sem confirmação → lança ValueError
author.delete()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

# Com confirmação → executa
author.delete(confirm=True)
```

### Prévia de QuerySet

```python
summary = Author.objects.filter(active=False).preview_delete()
```

### Exclusão segura de QuerySet

Use `delete_with_preview()` — o `.delete()` padrão do Django **não é sobrescrito** nesta biblioteca,
para não quebrar o Django admin e outras operações internas do framework.

```python
# Sem confirmação → lança ValueError
Author.objects.filter(active=False).delete_with_preview()

# Com confirmação → executa
Author.objects.filter(active=False).delete_with_preview(confirm=True)

# O .delete() padrão continua funcionando normalmente (sem proteção)
Author.objects.filter(active=False).delete()
```

### Comando de gerenciamento

```bash
# Prévia (saída em texto)
python manage.py preview_delete myapp.Author 1

# Prévia (saída em JSON)
python manage.py preview_delete myapp.Author 1 --format json

# Prévia + execução
python manage.py preview_delete myapp.Author 1 --execute
```

### Formato de saída JSON

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

## Configuração

```python
# settings.py — número máximo de representações de itens por modelo (padrão: 100)
DELETE_PREVIEW_MAX_ITEMS = 50
```

## Limitações

- Não suporta exclusão suave — os objetos são excluídos permanentemente
- Não faz prévia de efeitos colaterais dos sinais `pre_delete` / `post_delete`
- `fast_deletes` (objetos excluídos sem carregamento em memória) são contados, mas podem incluir representações aproximadas via `str()`

## Aplicação de exemplo

O repositório inclui um projeto Django completo e executável em `example/` que
demonstra todas as funcionalidades da biblioteca usando um domínio de livraria
(`Author`, `Book`, `Order`, `Publisher`).

### Configuração

```bash
git clone https://github.com/adrianomargarin/django-delete-preview
cd django-delete-preview
pip install -e ".[dev]"

cd example
python manage.py migrate
python manage.py loaddata initial_data   # carrega 3 autores, 9 livros, 5 pedidos, 3 editoras
```

### Prévia de instância

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

### Exclusão segura de instância

```python
author.delete()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

author.delete(confirm=True)
# (6, {"bookstore.Book": 3, "bookstore.Order": 2, "bookstore.Author": 1})
```

### Prévia de QuerySet

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

### Exclusão segura de QuerySet

```python
Author.objects.all().delete_with_preview()
# ValueError: Delete blocked. Run preview_delete() first and confirm the operation.

Author.objects.all().delete_with_preview(confirm=True)
# (20, {"bookstore.Book": 9, "bookstore.Order": 5, "bookstore.Author": 3})
```

### Comando de gerenciamento

```bash
# Prévia em texto legível
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

# Prévia em JSON
python manage.py preview_delete bookstore.Author 1 --format json

# Prévia e execução
python manage.py preview_delete bookstore.Author 1 --execute
```

### Publisher (sem cascata)

`Publisher` não possui modelos relacionados, então excluir um afeta apenas ele mesmo:

```python
from bookstore.models import Publisher

pub = Publisher.objects.get(pk=1)
pub.preview_delete()
# {"database": "default", "total_objects": 1, "models": {"bookstore.Publisher": 1}, ...}

pub.delete(confirm=True)
```

## Configuração de desenvolvimento

```bash
git clone https://github.com/adrianomargarin/django-delete-preview
cd django-delete-preview
pip install -e ".[dev]"
pre-commit install

# Executar testes
pytest

# Lint
ruff check src tests

# Verificação de tipos
mypy src/django_delete_preview
```
