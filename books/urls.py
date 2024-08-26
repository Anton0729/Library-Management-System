from django.urls import path

from .views import Books

urlpatterns = [
    path("books/", Books.as_view(), name="books-list-create"),
    path("books/<int:pk>/", Books.as_view(), name="books-detail"),
]