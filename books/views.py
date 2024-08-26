from django.shortcuts import render, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Book
from .serializer import BookSerializer
from .filters import BookFilter

PAGE_SIZE = 10
MAX_PAGE_SIZE = 1000
PAGE_SIZE_PARAM_NAME = "page_size"


class BookListPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = PAGE_SIZE_PARAM_NAME
    max_page_size = MAX_PAGE_SIZE


class Books(APIView):
    """
    API for managing Books
    """
    pagination_class = BookListPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookFilter

    def get(self, request, pk=None):
        """
        Retrieve details of a book or a list of all books

        If a primary key (pk) is provided, retrieve details of a specified book.
        If no pk is provided, retrieves a list of all books.

        :param request: HTTP request object
        :param pk: Optional primary key of the book to retrieve details (default: None)
        :return: Serialized data of book(s) or error message if not found.
        """
        if pk:
            try:
                book = Book.objects.get(pk=pk)
                book_serializer = BookSerializer(book)
                return Response(book_serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"error": f"Book with id {pk} not found"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            books = Book.objects.all()

            # Apply filtering
            filterset = self.filter_class(data=request.GET, queryset=books)
            if not filterset.is_valid():
                return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
            filtered_books = filterset.qs

            # Pagination
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(filtered_books, request)
            book_serializer = BookSerializer(result_page, many=True)
            return paginator.get_paginated_response(book_serializer.data)


    def post(self, request):

        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing book.

        Retrieves the book with the specified primary key (pk) and updates its data with the provided request data.

        :param request: HTTP request object containing updated data for the book.
        :param pk: Primary key of the book to be updated
        :return: Serialized data of the updated book or error message if not found or validation fails
        """
        try:
            book = Book.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": f"Book with id {pk} not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookSerializer(book, data=request.data, partial=True)  # partial=True to allow partial updates.
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete an existing book.

        Delete the book with the specified primary key (pk).

        :param request: HTTP request object
        :param pk: Primary key of the book to be deleted
        :return: Success message if deleted or error message if not found.
        """
        try:
            book = Book.objects.get(pk=pk)
            book.delete()
            return Response({"message": "Book deleted successfully"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": f"Book with id {pk} not found"}, status=status.HTTP_400_BAD_REQUEST)
