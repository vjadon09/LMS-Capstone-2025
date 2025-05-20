from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl, field_validator
from .database.db import *
from typing import List

app = FastAPI()
router = APIRouter()
db = get_db()

def normalize_bson(book: dict) -> dict:
    if "_id" in book:
        del book["_id"]

    fields = ["pageNumber", "numCopies", "numOfMins"]
    for field in fields:
        if isinstance(book.get(field), dict) and "$numberInt" in book[field]:
            book[field] = int(book[field]["$numberInt"])
        else:
            book[field] = int(book.get(field, 0))  # Default to 0 if missing

    if isinstance(book.get("kidFriendly"), dict) and "$numberInt" in book["kidFriendly"]:
        book["kidFriendly"] = bool(book["kidFriendly"]["$numberInt"])
    else:
        book["kidFriendly"] = book.get("kidFriendly", False)  # Default to False if missing

    return book

class Book(BaseModel):
    title: str
    author: str
    genre: str
    rating: float
    kidFriendly: bool
    description: str
    format: str
    pageNumber: int
    publisher: str
    status: str
    isbn: str
    numOfMins: int
    numCopies: int

class BookImages(BaseModel):
    _id: str
    bookISBN: str
    imageURL: HttpUrl
    
class Reservations(BaseModel):
    reservation_id: str
    user_email: str
    book_id: str
    reservation_date: str
    expiration_date: str
    status: str
    user_id: str
    isbn: str
    
    @field_validator('reservation_id', 'user_id', mode='before')
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator('reservation_date', 'expiration_date', mode='before')
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        

@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    book_data = db["books"].find_one({"isbn": isbn})
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(**normalize_bson(book_data))

@router.get("/books", response_model=List[Book])
def list_books():
    db = get_db()
    books = list(db["books"].find())
    return [Book(**book) for book in books]


'''Search Bar Queries'''
# Get a list of books by title
@app.get("/books/{title}", response_model=List[Book])
def get_books_by_title(title: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"title": {"$regex": title, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books


# Get a list of books by author
@app.get("/books/{author}", response_model=List[Book])
def get_books_by_author(author: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"author": {"$regex": author, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books

# Get a list of books with a rating greater than or equal to the given rating
@app.get("/books/rating/{rating}", response_model=List[Book])
def get_books_by_rating(rating: float):
    # Adding the 'i' flag for case-insensitive matching isn't necessary for numeric comparisons
    books_cursor = db["books"].find({"rating": {"$gte": rating}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books

# Get a list of books by publisher
@app.get("/books/{publisher}", response_model=List[Book])
def get_books_by_publisher(publisher: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"publisher": {"$regex": publisher, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books


# Get a list of books by genre
@app.get("/books/{genre}", response_model=List[Book])
def get_books_by_genre(genre: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"genre": {"$regex": f"^\s*{genre}$", "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books

# Get a list of books by isbn
@app.get("/books/{isbn}", response_model=List[Book])
def get_books_by_isbn(isbn: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"isbn": {"$regex": isbn, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books

# Get a list of books by status
@app.get("/books/{status}", response_model=List[Book])
def get_books_by_status(status: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"status": {"$regex": status, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books


# Get a list of books by format
@app.get("/books/{format}", response_model=List[Book])
def get_books_by_format(format: str):
    # Adding the 'i' flag for case-insensitive matching
    books_cursor = db["books"].find({"format": {"$regex": format, "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books


# Get a list of books by audience (kid-friendly)
@app.get("/books/{kidFriendly}", response_model=List[Book])
def get_books_by_audience(kidFriendly: bool):
    # Adding the 'i' flag for case-insensitive matching if the field is a string
    books_cursor = db["books"].find({"kidFriendly": {"$regex": str(kidFriendly), "$options": "i"}})
    books = [Book(**normalize_bson(book)) for book in books_cursor]
    return books

@app.get("/newest-books", response_model=List[Book])
def get_newest():
    books = db["books"].find()
    books_list = list(books)
    return books_list[-10:]

@app.get("/popular-books", response_model=List[Book])
def get_popular():
    books = db["books"].find().sort("rating", -1).limit(10)
    books_list = list(books)
    return books_list

# handling Placing a hold logic

@app.put("/books/decr/{isbn}")
def decr_book_copies(isbn: int):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return False
    result = db["books"].update_one({"isbn": isbn}, {"$inc": {"numCopies": -1}})

    if result.modified_count > 0:
        return True
    else:
        return False
    
@app.put("/books/incr/{isbn}")
def incr_book_copies(isbn: int):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return JSONResponse(status_code=404, content={"message": "Book on hold is not found"})

    result = db["books"].update_one({"isbn": isbn}, {"$inc": {"numCopies": 1}})
    if result.modified_count > 0:
        return JSONResponse(status_code=200, content={"message": "Copy successfully returned!"})
    else:
        return JSONResponse(status_code=500, content={"message": "Failed to update book for reservation."})
    
@app.get("/books/{isbn}")
def get_book_copies(isbn: int):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return None
    book["_id"] = str(book["_id"])

    if isinstance(book["numCopies"], dict) and "$numberInt" in book["numCopies"]:
        book["numCopies"] = int(book["numCopies"]["$numberInt"])

    return book["numCopies"]