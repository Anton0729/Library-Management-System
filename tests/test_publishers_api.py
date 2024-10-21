from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_user

client = TestClient(app)


def test_create_publisher_successful(create_user):
    """
    Test case to create new publisher
    """
    publisher_data = {"name": "Penguin Books", "established_year": 1935}
    response = client.post(
        "/publishers",
        json=publisher_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == publisher_data["name"].lower()


def test_create_publisher_duplicate(create_user):
    """
    Test case for creating duplicate publisher.
    """
    publisher_data = {"name": "Penguin Books", "established_year": 1935}
    client.post(
        "/publishers",
        json=publisher_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    # New request with duplicate name
    response = client.post(
        "/publishers",
        json=publisher_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Publisher '{publisher_data['name']}' already exists."
    }


def test_create_publisher_with_invalid_data(create_user):
    """
    Test case for creating publisher with invalid data.
    """
    publisher_data = {"name": "Penguin Books", "established_year": 2030}
    response = client.post(
        "/publishers",
        json=publisher_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    assert response.status_code == 422


def test_get_publishers_no_data(create_user):
    """
    Test case for retrieving publishers without data.
    """
    response = client.get(
        "/publishers", headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No publishers found."}


def test_get_publishers_with_data(create_user):
    """
    Test case for retrieving publishers with existed data.
    """
    publisher_data = {"name": "Penguin Books", "established_year": 1900}
    client.post(
        "/publishers",
        json=publisher_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    response = client.get(
        "/publishers", headers={"Authorization": f"Bearer {create_user}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == publisher_data["name"].lower()
