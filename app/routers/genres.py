from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from typing import List

from app.dependencies import get_db
from app.models import Genre
from app.models import User as UserModel
from app.schemas import GenreResponse, GenreCreate
from auth.dependencies import get_current_user

router = APIRouter()


@router.get("/genres", response_model=List[GenreResponse], status_code=200)
def get_genres(
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    genres = session.query(Genre).all()

    if not genres:
        raise HTTPException(status_code=404, detail="No genres found.")

    return genres


@router.post("/genres", response_model=GenreResponse, status_code=201)
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
