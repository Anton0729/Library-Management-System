from .models import Book
import django_filters


class BookFilter(django_filters.FilterSet):
    # lookup_expr='icontains' option allows for case-insensitive partial matches.
    # lookup_expr='exact' option allows for exact matches.
    author = django_filters.CharFilter(lookup_expr='icontains')
    published_date = django_filters.DateFilter(lookup_expr='exact')
    language = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['author', 'published_date', 'language']