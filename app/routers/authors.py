from typing import List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Book, Author
from app.models import User as UserModel
from app.schemas import BookResponse, AuthorCreate, AuthorResponse
from auth.dependencies import get_current_user

router = APIRouter()


@router.get("/authors/{id}/books", response_model=List[BookResponse], status_code=200)
def get_author_books(
        id: int,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    # Check if author exists.
    author = session.query(Author).filter(Author.id == id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    books = session.query(Book).filter(Book.author_id == id).all()

    return books


@router.post("/authors", response_model=AuthorResponse, status_code=201)
def create_author(
        author: AuthorCreate,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    # Check that author's name is not already exists
    existing_author = session.query(Author).filter(Author.name == author.name).first()
    if existing_author:
        raise HTTPException(
            status_code=400, detail=f"Author {author.name} already exists."
        )

    new_author = Author(
        name=author.name,
        birthdate=author.birthdate,
    )

    session.add(new_author)
    session.commit()
    session.refresh(new_author)

    return new_author
