import re
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, field_validator


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    username: str

    class Config:
        orm_mode = True


class BookCreate(BaseModel):
    title: str
    isbn: str
    author_id: int
    genre_id: int
    publisher_id: Optional[int] = None
    publish_date: date
    available: bool = True

    @field_validator("isbn")
    def validate_isbn(cls, v):
        # ISBN-10 or ISBN-13 regex pattern
        isbn_pattern = re.compile(
            r"^(97(8|9)?[\s-]?)?\d{1,5}[\s-]?\d{1,7}[\s-]?\d{1,6}[\s-]?\d{1}$|^(97(8|9)?[\s-]?)?\d{9}(\d|X)$"
        )
        if not isbn_pattern.match(v):
            raise ValueError("Invalid ISBN format. Must be ISBN-10 or ISBN-13.")
        return v

    @field_validator("publish_date")
    def validate_publish_date(cls, v):
        if v >= date.today():
            raise ValueError("Publish date must be in the past.")
        return v


class BookResponse(BookCreate):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class PaginationInfo(BaseModel):
    page: int
    size: int
    total: int


class BookResponsePagination(BaseModel):
    pagination: PaginationInfo
    tasks: List[BookResponse]


class AuthorCreate(BaseModel):
    name: str
    birthdate: date

    @field_validator("birthdate")
    def validate_birthdate(cls, v):
        if v > date.today():
            raise ValueError("Birthdate cannot be in the future.")
        return v

    class Config:
        orm_mode = True


class AuthorResponse(AuthorCreate):
    id: int

    class Config:
        orm_mode = True


class PublisherCreate(BaseModel):
    name: str
    established_year: int

    @field_validator("established_year")
    def validate_established_year(cls, v):
        if v >= date.today().year:
            raise ValueError("Established year must be in past.")
        return v

    class Config:
        orm_mode = True


class PublisherResponse(PublisherCreate):
    id: int

    class Config:
        orm_mode = True


class GenreCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GenreResponse(GenreCreate):
    id: int

    class Config:
        orm_mode = True


class BorrowingHistoryCreate(BaseModel):
    book_id: int

    class Config:
        orm_mode = True


class BorrowingHistoryResponse(BaseModel):
    id: int
    user: UserResponse
    book: BookResponse
    borrow_date: date
    return_date: Optional[date] = None

    class Config:
        orm_mode = True


class ReturnRequestCreate(BaseModel):
    book_id: int
    return_date: date = date.today()

    class Config:
        orm_mode = True


class ReturnRequestResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    borrow_date: date
    return_date: date

    class Config:
        orm_mode = True
