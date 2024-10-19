from typing import List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation

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
    """
    Retrieve all publishers in the library.

    Returns
    -------
    - **return**: A list of all publishers in the library.
    """
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
    """
    Add a new publisher to the library.

    Request Body
    ------------
    - **name** (string): The name of the publisher. Must be unique.
    - **established_year** (integer): The year the publisher was established.

    Example Request Body
    --------------------

    ```json
    {
      "name": "Penguin Books",
      "established_year": 1935
    }
    ```

    Returns
    -------
    - **return**: The created publisher's details.
    """
    publisher = (
        session.query(Publisher)
        .filter(Publisher.name == publisher_data.name.lower())
        .first()
    )

    if publisher:
        raise HTTPException(
            status_code=400, detail=f"Publisher '{publisher_data.name}' already exists."
        )

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
        raise HTTPException(
            status_code=400, detail=f"Integrity error: {str(e.orig)}"
        ) from e
    except DataError as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(
            status_code=400, detail=f"Data error: {str(e.orig)}"
        )
    except UniqueViolation as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(
            status_code=400, detail=f"Unique error: {str(e.orig)}"
        ) from e
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=400, detail=f"Value error: {str(e)}"
        ) from e

    except Exception as e:
        session.rollback()  # Roll back the session in case of error
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        ) from e

    return new_publisher
