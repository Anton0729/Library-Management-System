from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_signup_successful():
    """
    Test case for user signup.
    """
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]


def test_signup_duplicate_username():
    """
    Test case for attempting to sign up with an already registered username.
    """
    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/auth/signup", json=user_data)  # First, create the user
    response = client.post(
        "/auth/signup", json=user_data
    )  # Attempt to create the same user again
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}


def test_login_successful():
    """
    Test case for successful login and token generation.
    """
    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/auth/signup", json=user_data)  # Ensure the user exists
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_unsuccessful():
    """
    Test case for login with incorrect credentials.
    """
    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/auth/signup", json=user_data)  # Ensure the user exists
    login_data = {"username": "wronguser", "password": "wrongpassword"}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
