from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_user, create_book

client = TestClient(app)


def test_get_book_history(create_user, create_book):
    """
    Test case for retrieving the borrowing history of a specific book.
    """
    book_id = create_book["id"]
    response = client.get(
        f"/books/{book_id}/history", headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 200


def test_get_no_book_history(create_user):
    """
    Test case for retrieving the borrowing history but with wrong book_id.
    """
    response = client.get(
        "/books/1/history", headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}


def test_get_books(create_user, create_book):
    """
    Test case for retrieving all books.
    """
    response = client.get(f"/books", headers={"Authorization": f"Bearer {create_user}"})
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert isinstance(response.json()["tasks"], list)


def test_get_books_no_data(create_user):
    """
    Test case for retrieving all books without data in response.
    """
    response = client.get(f"/books", headers={"Authorization": f"Bearer {create_user}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No books found."}


def test_create_book_author_not_found(create_user):
    """
    Test case with wrong author_id
    """
    genre_data = {"name": "Science Fiction"}
    genre_response = client.post(
        "/genres", json=genre_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    book_data = {
        "title": "Another Book",
        "isbn": "0-19-853454-3",
        "author_id": 999,  # Invalid author ID
        "genre_id": genre_response.json()["id"],
        "publisher_id": None,
        "publish_date": "2024-10-14",
    }

    response = client.post(
        "/books", json=book_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found."}


def test_create_book_genre_not_found(create_user):
    """
    Test case with wrong genre_id
    """
    author_data = {"name": "Jane Austen", "birthdate": "1960-01-01"}
    author_response = client.post(
        "/authors", json=author_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    book_data = {
        "title": "Another Book",
        "isbn": "0-19-853454-3",
        "author_id": author_response.json()["id"],
        "genre_id": 999,  # Invalid author ID
        "publisher_id": None,
        "publish_date": "2024-10-14",
    }

    response = client.post(
        "/books", json=book_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Genre not found."}
