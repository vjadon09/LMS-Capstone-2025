from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from .database.db import *
from typing import List
from fastapi.responses import JSONResponse

app = FastAPI()

class Book(BaseModel):
    title: str
    isbn: str
    author: str
    genre: str
    rating: float
    kidFriendly: bool
    description: str
    format: str
    pageNumber: int
    bookID: str
    publisher: str
    status: str

@app.get("/books/titles", response_model=str)
def get_book_by_isbn(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    return book["title"]

@app.get("/books/formats", response_model=str)
def get_book_format_by_isbn(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    return book["format"]