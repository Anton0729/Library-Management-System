from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models import User
from app.config import settings
from auth.models import TokenData
from auth.utils import verify_password
from app.dependencies import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Get a user from the database by username
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Authenticate the user by verifying credentials
def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user(db, username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


# Get the currently logged-in user from the JWT token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user
