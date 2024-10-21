# Library Management System API

## Overview

This project is a library management system built with FastAPI and PostgreSQL, enabling users to manage library books
and includes user authentication with JWT. The system allows users to manage library books, authors, genres,
and borrow/return actions. It supports sorting by title, author, publish date; pagination, and ensures that 
only authorized users can access the service. 
The application is fully Dockerized for easy setup and deployment.

You can find the API documentation in the following link: [Link](https://drive.google.com/file/d/1euuTm4GmwqqPT9e3e7NGLQs_kAPKqdP_/view?usp=sharing)
<br>
Additionally, you can find the documentation in Swagger at the following URL: `http://localhost:8000/docs`

## Features

1. **FastAPI with PostgreSQL Setup**
2. **Operations for Managing Library Books**
   - Get a list of all books
   - Create a new book
   - Get the borrowing history of a specific book
   - List all books written by a specific author
   - Create a new author
   - Borrow and return books (can be returned only by a borrower)
   - Get al genres
   - Create a new genre
   - Get all publishers
   - Create a new publisher
3. **Book Sorting and Pagination**
   - Sort books by one of the field (title, author, publish date)
5. **Docker Container with Docker Compose**
6. **JWT User Authentication and Authorization**
7. **Writing Unit Tests with Coverage**
    - Unit tests for API endpoints
    - Coverage tool to check the percentage of test coverage using
8. **Manage Migrations with Alembic**


## <ins> Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/Anton0729/Library-Management-System.git
cd .\Library-Management-System\
```

### 2. Run Docker Desktop

### 3. Build and run the container

```bash
docker-compose up --build
```

### 4. Apply All Migrations
Make sure all migrations are applied:
```bash
docker-compose exec web alembic upgrade head 
```

### 5. Access the Application

- Application: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Delete the container

```bash
docker-compose down
```

<br>

### Running Tests:

To run tests for this project, follow these steps:

### 1. Ensure the test database is created

Make sure the web container is running before creating the test database before running the tests. You can do this using
the following command:

```bash
docker-compose exec db psql -U postgres -c "CREATE DATABASE test_todo_db;"
```

### 2. Run the tests

Once the test database is set up, you can run the tests using the following command:

```bash
docker-compose run --rm web sh -c "pytest"
```

### 3. Test Coverage:

To check the test coverage, follow these steps:

```bash
docker-compose run --rm web sh -c "coverage run -m pytest && coverage report"
```
