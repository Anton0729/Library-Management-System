import datetime

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Book, BorrowingHistory
from app.models import User as UserModel
from app.schemas import (
    BorrowingHistoryCreate,
    BorrowingHistoryResponse,
    ReturnRequestCreate,
    ReturnRequestResponse,
)
from auth.dependencies import get_current_user

router = APIRouter()

MAX_BORROW_LIMIT = 5


@router.post("/borrow", response_model=BorrowingHistoryResponse, status_code=201)
def borrow_book(
    borrow_data: BorrowingHistoryCreate,
    session: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Borrow a book from the library.

    Request Body
    ------------
    - **book_id** (integer): The ID of the book to be borrowed.

    Example Request Body
    --------------------
    ```json
    {
      "book_id": 1
    }
    ```

    Returns
    -------
    - **return**: A detailed record of the borrowing event.
    """
    # Check if the book exists and available
    book = session.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book or not book.available:
        raise HTTPException(status_code=400, detail="Book is not available for borrowing.")

    # Check if user has already borrowed the same book and hasn't returned it yet
    active_borrow = session.query(BorrowingHistory).filter(
        BorrowingHistory.user_id == current_user.id,
        BorrowingHistory.book_id == borrow_data.book_id,
        BorrowingHistory.return_date.is_(None)
    ).first()

    if active_borrow:
        raise HTTPException(status_code=400, detail="You have already borrowed this book and have not returned it yet.")

    # Check if user has reached maximum number of borrowed books
    borrowed_books = (
        session.query(BorrowingHistory)
        .filter(
            BorrowingHistory.user_id == current_user.id,
            BorrowingHistory.return_date.is_(None),
        )
        .count()
    )

    if borrowed_books >= MAX_BORROW_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot borrow more than {MAX_BORROW_LIMIT} books.",
        )

    # Borrow book
    new_borrow = BorrowingHistory(
        book_id=borrow_data.book_id,
        user_id=current_user.id,
        borrow_date=datetime.date.today(),
    )

    try:
        session.add(new_borrow)
        session.commit()
        session.refresh(new_borrow)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error occurred while borrowing the book: {str(e)}"
        ) from e

    return new_borrow


@router.post("/return", response_model=ReturnRequestResponse, status_code=201)
def return_book(
    return_data: ReturnRequestCreate,
    session: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return a borrowed book to the library.

    Request Body
    ------------
    - **book_id** (integer): The ID of the book being returned.
    - **return_date** (date): The date the book is being returned.

    Example Request Body
    --------------------
    ```json
    {
      "book_id": 1,
      "return_date": "2024-10-10"
    }
    ```

    Returns
    -------
    - **return**: A detailed record of the return event, including book ID, user ID, borrow date, and return date.
    """
    borrowing_record = (
        session.query(BorrowingHistory)
        .filter(
            BorrowingHistory.book_id == return_data.book_id,
            BorrowingHistory.user_id == current_user.id,
            BorrowingHistory.return_date.is_(None),
        )
        .first()
    )

    if not borrowing_record:
        raise HTTPException(status_code=400, detail="No active borrowed books found.")

    borrowing_record.return_date = return_data.return_date

    session.commit()

    return ReturnRequestResponse(
        id=borrowing_record.id,
        book_id=borrowing_record.book_id,
        user_id=borrowing_record.user_id,
        borrow_date=borrowing_record.borrow_date,
        return_date=borrowing_record.return_date,
    )
