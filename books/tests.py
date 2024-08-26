from django.urls import reverse
from .models import Book
from rest_framework.test import APITestCase
from rest_framework import status


class BookAPITests(APITestCase):
    def setUp(self):
        # Set up some initial data
        self.book1 = Book.objects.create(
            title="Book One",
            author="Author One",
            published_date="2023-01-01",
            isbn="1234567890123",
            pages=200,
            cover="http://example.com/cover1.jpg",
            language="English"
        )
        self.book2 = Book.objects.create(
            title="Book Two",
            author="Author Two",
            published_date="2024-01-01",
            isbn="9876543210987",
            pages=300,
            cover="http://example.com/cover2.jpg",
            language="French"
        )
        self.books_url = reverse('books-list-create')
        self.detail_url = lambda pk: reverse('books-detail', kwargs={'pk': pk})

    def test_get_books_list(self):
        response = self.client.get(self.books_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_filtered_books(self):
        url = f"{self.books_url}?author=Author One"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Book One")

    def test_get_paginated_books(self):
        url = f"{self.books_url}?page_size=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_book_detail(self):
        response = self.client.get(self.detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Book One")

    def test_get_book_not_found(self):
        response = self.client.get(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Book with id 9999 not found")

    def test_create_book(self):
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'published_date': '2024-12-31',
            'isbn': '1112233445566',
            'pages': 150,
            'cover': 'http://example.com/new_cover.jpg',
            'language': 'Spanish'
        }
        response = self.client.post(self.books_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Book')

    def test_create_book_unsuccessful(self):
        data = {}
        response = self.client.post(self.books_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_book(self):
        data = {'title': 'Updated Book Title'}
        response = self.client.put(self.detail_url(self.book1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Book Title')

    def test_update_book_not_found(self):
        non_existent_book_id = 9999
        response = self.client.put(self.detail_url(non_existent_book_id), {'title': 'Some Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], f"Book with id {non_existent_book_id} not found")

    def test_delete_book(self):
        response = self.client.delete(self.detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Book deleted successfully")
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())

    def test_update_book_invalid_data(self):
        invalid_data = {
            'title': '',  # Assuming title cannot be empty
        }
        response = self.client.put(self.detail_url(self.book1.id), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_delete_book_not_found(self):
        response = self.client.delete(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Book with id 9999 not found")
