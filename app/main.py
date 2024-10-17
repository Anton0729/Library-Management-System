from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi_pagination import add_pagination

from sqlalchemy.orm import selectinload, Session
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation
from sqlalchemy.future import select

from typing import Optional, List

from app.dependencies import get_db
from app.models import User, Book, Genre, Author, Publisher
from app.models import User as UserModel
from app.schemas import BookCreate, BookResponse, BookResponsePagination, AuthorCreate, AuthorResponse, PublisherCreate, \
    PublisherResponse, GenreResponse, GenreCreate
from auth.dependencies import get_current_user
from auth.routes import router as auth_router

app = FastAPI(
    title="Library Management System"
)

# Include authentication routes from the auth module
app.include_router(auth_router, prefix="/auth", tags=["auth"])


# def get_user_or_404()

@app.get("/authors/{id}/books", response_model=List[BookResponse], status_code=200)
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


@app.post("/authors/", response_model=AuthorResponse, status_code=201)
def create_author(
        author: AuthorCreate,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    # Check that author's name is not already exists
    existing_author = session.query(Author).filter(Author.name == author.name).first()
    if existing_author:
        raise HTTPException(status_code=400, detail=f"Author {author.name} already exists.")

    new_author = Author(
        name=author.name,
        birthdate=author.birthdate,
    )

    session.add(new_author)
    session.commit()
    session.refresh(new_author)

    return new_author


@app.get("/books/", response_model=BookResponsePagination, status_code=200)
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


@app.post("/books/", response_model=BookResponse, status_code=201)
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


@app.get("/publishers/", response_model=List[PublisherResponse], status_code=200)
def get_publishers(
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    publishers = session.query(Publisher).all()

    if not publishers:
        raise HTTPException(status_code=404, detail="No publishers found.")

    return publishers


@app.post("/publishers/", response_model=PublisherResponse, status_code=201)
def create_publisher(
        publisher_data: PublisherCreate,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    publisher = session.query(Publisher).filter(Publisher.name == publisher_data.name.lower()).first()

    if publisher:
        raise HTTPException(status_code=400, detail=f"Publisher '{publisher_data.name}' already exists.")

    new_publisher = Publisher(
        name=publisher_data.name.lower(),
        established_year=publisher_data.established_year,
    )
    try:
        session.add(new_publisher)
        session.commit()
        session.refresh(new_publisher)
    except IntegrityError as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Integrity error: {}".format(str(e.orig)))
    except DataError as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Data error: {}".format(str(e.orig)))
    except UniqueViolation as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=400, detail="Unique error: {}".format(str(e.orig)))
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail="Value error: {}".format(str(e.orig)))

    except Exception as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(status_code=500, detail="An unexpected error occurred: {}".format(str(e)))


    return new_publisher


@app.get("/genres/", response_model=List[GenreResponse], status_code=200)
def get_genres(
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    genres = session.query(Genre).all()

    if not genres:
        raise HTTPException(status_code=404, detail="No genres found.")

    return genres


@app.post("/genres/", response_model=GenreResponse, status_code=201)
def create_genre(
        genre_data: GenreCreate,
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    genres = session.query(Genre).filter(Genre.name == genre_data.name.lower()).first()

    if genres:
        raise HTTPException(status_code=400, detail=f"Genre '{genre_data.name}' already exists.")

    new_genre = Genre(
        name=genre_data.name.lower()
    )
    session.add(new_genre)
    session.commit()
    session.refresh(new_genre)

    return new_genre



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
