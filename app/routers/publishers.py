from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation

from typing import List

from app.dependencies import get_db
from app.models import Publisher
from app.models import User as UserModel
from app.schemas import PublisherCreate, PublisherResponse
from auth.dependencies import get_current_user

router = APIRouter()


@router.get("/publishers", response_model=List[PublisherResponse], status_code=200)
def get_publishers(
        session: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    publishers = session.query(Publisher).all()

    if not publishers:
        raise HTTPException(status_code=404, detail="No publishers found.")

    return publishers


@router.post("/publishers", response_model=PublisherResponse, status_code=201)
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
