from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_user, create_book

client = TestClient(app)


def test_borrow_book_success(create_user, create_book):
    """
    Test case successful borrowing of a book.
    """
    borrow_data = {"book_id": 1}
    response = client.post(
        "/borrow", json=borrow_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    assert response.status_code == 201
    assert response.json()["book"]["id"] == borrow_data["book_id"]


def test_borrow_book_not_found(create_user, create_book):
    """
    Test case to borrow not found book.
    """
    borrow_data = {"book_id": 9999}
    response = client.post(
        "/borrow",
        json=borrow_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Book is not available for borrowing."


def test_borrow_book_already_borrowed(create_user, create_book):
    """
    Test case to borrow already borrowed book
    """
    borrow_data = {"book_id": create_book["id"]}
    client.post(
        "/borrow", json=borrow_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    response = client.post(
        "/borrow",
        json=borrow_data,
        headers={"Authorization": f"Bearer {create_user}"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "You have already borrowed this book and have not returned it yet."
    )


def test_return_book_success(create_user, create_book):
    """
    Test successful return of a book.
    """
    borrow_data = {"book_id": 1}
    client.post(
        "/borrow", json=borrow_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    return_data = {"book_id": 1, "return_date": "2024-10-20"}
    response = client.post(
        "/return", json=return_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    assert response.status_code == 201
    assert response.json()["return_date"] == return_data["return_date"]


def test_return_book_not_borrowed(create_user, create_book):
    """
    Test that returning a book that was not borrowed results in an error.
    """
    # Try to return a book that was never borrowed
    return_data = {"book_id": 1, "return_date": "2024-10-20"}
    response = client.post(
        "/return", json=return_data, headers={"Authorization": f"Bearer {create_user}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No active borrowed books found."
