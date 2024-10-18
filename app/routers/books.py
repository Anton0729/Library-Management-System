from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation
from sqlalchemy.future import select

from typing import Optional, List

from app.dependencies import get_db
from app.models import Book, Genre, Author, BorrowingHistory
from app.models import User as UserModel
from app.schemas import BookCreate, BookResponse, BookResponsePagination, BorrowingHistoryResponse

from auth.dependencies import get_current_user

router = APIRouter()


@router.get("/books/{id}/history", response_model=List[BorrowingHistoryResponse], status_code=200)
def get_borrowing_history(
        id: int,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    # Check if book exists
    book_history = session.query(Book).filter(Book.id == id).first()
    if not book_history:
        raise HTTPException(status_code=404, detail="Book not found.")

    # Get all history of book
    book_history = session.query(BorrowingHistory).filter(BorrowingHistory.book_id == id).all()
    return book_history


@router.get("/books", response_model=BookResponsePagination, status_code=200)
def get_books(
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
        page: int = Query(1, ge=1),  # Page number, default is 1
        size: int = Query(10, ge=1, le=100),  # Page size, default is 10, max 100
        sort_by: Optional[str] = Query(None, enum=["title", "author", "publish_date"])
):
    """
    Retrieve a paginated list of books with optional sorting by title, author, or publish_date

    - **page**: Page number to retrieve (default is 1).
    - **size**: Number of tasks per page (default is 10, max 100).
    - **sort_by**: Field to sort by (title, author, or publish_date).
    """

    offset = (page - 1) * size  # Calculate the offset for pagination
    query = select(Book)
    if sort_by:
        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "author":
            query = query.join(Author).order_by(Author.name)
        elif sort_by == "publish_date":
            query = query.order_by(Book.publish_date)

    # apply pagination
    query = query.offset(offset).limit(size)

    result = session.execute(query)
    books = result.scalars().all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found.")

    book_responses = [BookResponse.from_orm(book) for book in books]

    # Build pagination info
    pagination_info = {
        "page": page,
        "size": size,
        "total": len(books),
    }

    return {
        "pagination": pagination_info,
        "tasks": book_responses,
    }


@router.post("/books", response_model=BookResponse, status_code=201)
def create_book(
        book: BookCreate,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    # Check if author exists.
    author = session.query(Author).filter(Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Check if genre exists.
    genre = session.query(Genre).filter(Genre.id == book.genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    # Create the new book record
    new_book = Book(
        title=book.title,
        isbn=book.isbn,
        author_id=book.author_id,
        genre_id=book.genre_id,
        publisher_id=book.publisher_id,
        publish_date=book.publish_date,
        available=book.available,
    )
    try:
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
    except IntegrityError as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Integrity error: {}".format(str(e.orig)))
    except DataError as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Data error: {}".format(str(e.orig)))
    except UniqueViolation as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Unique error: {}".format(str(e.orig)))
    except Exception as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=500, detail="An unexpected error occurred: {}".format(str(e)))

    return new_book
