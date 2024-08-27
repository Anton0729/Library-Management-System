# Library Management System API

This project is a RESTful API for managing a library of books, allowing users to add, edit, delete, and view books. The API also provides filtering, pagination, and CRUD operations.

## Features

- **CRUD Operations**:
  - Create a book
  - Retrieve a list of books
  - Retrieve detailed information about a book by ID
  - Update book information
  - Delete a book
- **Filtering**:
  - Filter books by author, published date, and language
- **Pagination**:
  - List books with pagination (10 books per page)
- **Testing**:
  - Unit tests for the main API endpoints

## Technology Stack

- **Framework**: Django 4.x
- **Database**: PostgreSQL
- **API**: Django REST Framework


## <ins> Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
https://github.com/Anton0729/Library-Management-System.git
cd .\Library-Management-System\
```

### 2. Run Docker Desktop

### 3. Build the container
```bash
docker-compose build
```

### 4. Run the container
```bash
docker-compose up -d
```

### 5. Apply migrations
To apply the database migrations, run:
```bash
docker-compose run --rm web sh -c "python manage.py migrate"
```

### 6. Create a superuser (optional, for Django admin):
```bash
docker-compose run --rm web sh -c "python manage.py createsuperuser"
```

### 7. Access the Application

- Application: http://localhost:8000


### 8. Delete the container
```bash
docker-compose down
```
<br>

### Running Tests:
Run tests using the following command:
```bash
docker-compose run --rm web sh -c "python manage.py test"
```

### Test Coverage:
To check the test coverage, follow these step:
```bash
docker-compose run --rm web sh -c "coverage run --source='.' manage.py test && coverage report"
```