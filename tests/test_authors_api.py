from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_user, create_book

client = TestClient(app)


def test_create_author_successful(create_user):
    """
    Test case to create author
    """
    author_data = {"name": "Jane Austen", "birthdate": "1960-01-01"}
    response = client.post(
        "/authors", json=author_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == author_data["name"]


def test_create_author_duplicate(create_user):
    """
    Test case for creating an author that already exists.
    """
    author_data = {"name": "Jane Austen", "birthdate": "1960-01-01"}
    client.post(
        "/authors", json=author_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    # Create post request with same author's name
    response = client.post(
        "/authors", json=author_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Author {author_data['name']} already exists."
    }


def test_create_author_with_invalid_data(create_user):
    """
    Test case for creating author with invalid data.
    """
    author_data = {"name": "Jane Austen", "birthdate": "2030-01-01"}
    response = client.post(
        "/authors", json=author_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 422


def test_get_author_no_books(create_user):
    """
    Test case for retrieving no books written by an author.
    """
    response = client.get(
        "/authors/1/books", headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found"}


def test_get_author_books(create_user, create_book):
    """
    Test case for retrieving books written by an author.
    """
    author_id = create_book["author_id"]
    response = client.get(
        f"/authors/{author_id}/books",
        headers={"Authorization": f"Bearer {create_user}"},
    )

    assert response.status_code == 200
    assert create_book["title"] == create_book["title"]
    assert create_book["isbn"] == create_book["isbn"]
    assert create_book["author_id"] == author_id
