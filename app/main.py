from fastapi import FastAPI

from auth.routes import router as auth_router
from app.routers.authors import router as author_router
from app.routers.books import router as book_router
from app.routers.borrow_return import router as borrow_return_router
from app.routers.genres import router as genre_router
from app.routers.publishers import router as publisher_router

app = FastAPI(
    title="Library Management System"
)

# Register the routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(author_router, tags=["author"])
app.include_router(book_router, tags=["book"])
app.include_router(borrow_return_router, tags=["borrow_return"])
app.include_router(genre_router, tags=["genre"])
app.include_router(publisher_router, tags=["publisher"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
