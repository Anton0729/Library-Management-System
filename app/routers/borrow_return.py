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
    # Check if the book exists and is available
    book = session.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book not available for borrowing.")

    # Check if the user has already borrowed the max allowed books
    borrowed_books_count = (
        session.query(BorrowingHistory)
        .filter(
            BorrowingHistory.user_id == current_user.id,
            BorrowingHistory.return_date is None,
        )
        .count()
    )

    if borrowed_books_count >= MAX_BORROW_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot borrow more than {MAX_BORROW_LIMIT} books.",
        )

    already_borrowed = session.query(BorrowingHistory).filter(
        BorrowingHistory.user_id == current_user.id,
        BorrowingHistory.book_id == borrow_data.book_id,
        BorrowingHistory.return_date is None,
    )

    if not already_borrowed:
        raise HTTPException(
            status_code=400,
            detail=f"You have already borrowed book {borrow_data.book_id}",
        )

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
    borrowing_record = (
        session.query(BorrowingHistory)
        .filter(
            BorrowingHistory.book_id == return_data.book_id,
            BorrowingHistory.user_id == current_user.id,
            BorrowingHistory.return_date is None,
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
