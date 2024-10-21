from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_user

client = TestClient(app)


def test_create_genre_successful(create_user):
    """
    Test case to create new genre
    """
    genre_data = {"name": "Science Fiction"}
    response = client.post(
        "/genres", json=genre_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == genre_data["name"].lower()


def test_create_genre_duplicate(create_user):
    """
    Test case for creating duplicate genre.
    """
    genre_data = {"name": "Science Fiction"}
    client.post(
        "/genres", json=genre_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    # Try again with same name
    response = client.post(
        "/genres", json=genre_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Genre '{genre_data['name']}' already exists."
    }


def test_get_genres_no_data(create_user):
    """
    Test case for retrieving genres without data.
    """
    response = client.get("/genres", headers={"Authorization": f"Bearer {create_user}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No genres found."}


def test_get_genres_with_data(create_user):
    """
    Test case for retrieving genres with existed data.
    """
    genre_data = {"name": "Science Fiction"}
    client.post(
        "/genres", json=genre_data, headers={"Authorization": f"Bearer {create_user}"}
    )
    response = client.get("/genres", headers={"Authorization": f"Bearer {create_user}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == genre_data["name"].lower()
