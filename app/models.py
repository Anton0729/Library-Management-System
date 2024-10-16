from sqlalchemy import Column, String, Integer, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    borrowing_history = relationship("BorrowingHistory", back_populates="user")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    birthdate = Column(Date)

    books = relationship("Book", back_populates="author")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates="genre")


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    established_year = Column(Integer)

    books = relationship("Book", back_populates="publisher")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    isbn = Column(String, unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    publish_date = Column(Date)
    available = Column(Boolean, default=True)

    author = relationship("Author", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    borrowing_history = relationship("BorrowingHistory", back_populates="book")


class BorrowingHistory(Base):
    __tablename__ = "borrowing_history"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    borrow_date = Column(Date, nullable=False)
    return_date = Column(Date)

    book = relationship("Book", back_populates="borrowing_history")
    user = relationship("User", back_populates="borrowing_history")
