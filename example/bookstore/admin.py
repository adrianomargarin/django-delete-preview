"""Admin registrations for the bookstore example app."""

from django.contrib import admin

from bookstore.models import Author, Book, Order, Publisher

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Publisher)
admin.site.register(Order)
