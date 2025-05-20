from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from .database.db import *
from typing import List
from fastapi.responses import JSONResponse

app = FastAPI()
router = APIRouter()

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
    numCopies: int
    numOfMins: int
    publisher: str
    status: str

# Create books
@app.post("/books/", response_model=dict)
def create_book(book: Book):
    book_dict = book.dict()
    result = db["books"].insert_one(book_dict)
    return {"id": str(result.inserted_id)}

# Get book information
@app.get("/title/{isbn}", response_model=str)
def get_book_title(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return ""
    return book["title"]

@app.get("/rating/{isbn}", response_model=str)
def get_book_rating(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return ""
    return book["rating"]