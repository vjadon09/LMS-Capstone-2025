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

@app.post("/books/", response_model=dict)
def create_book(book: Book):
    book_dict = book.dict()
    result = db["books"].insert_one(book_dict)
    return {"id": str(result.inserted_id)}

@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return None
    book["_id"] = str(book["_id"])

    if isinstance(book["pageNumber"], dict) and "$numberInt" in book["pageNumber"]:
        book["pageNumber"] = int(book["pageNumber"]["$numberInt"])
    if isinstance(book["rating"], dict) and "$numberInt" in book["rating"]:
        book["rating"] = float(book["rating"]["$numberInt"])
    if isinstance(book['kidFriendly'], dict) and "$numberInt" in book['kidFriendly']:
        book['kidFriendly'] = bool(book['kidFriendly']["$numberInt"])

    return Book(**book)

@app.get("/books/", response_model=List[Book])
def list_books():
    db = get_db()
    books = list(db["books"].find())
    return [Book(**book) for book in books]

@app.get("/books/title/{isbn}", response_model=str)
def get_book_title(isbn: str):
    db = get_db()
    book = db["books"].find_one({"isbn": isbn}, {"_id": 0, "title": 1})
    if not book:
        return "Book not found"
    return book["title"]

@app.delete("/books/{isbn}", response_model=dict)
def delete_book(isbn: str):
    result = db["books"].delete_one({"isbn": isbn})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully."}
    else:
        return {"message": "Error deleting book."}

# numCopies increment and decrement
@app.get("/books/{isbn}")
def get_book_copies(isbn: int):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return None
    book["_id"] = str(book["_id"])

    if isinstance(book["numCopies"], dict) and "$numberInt" in book["numCopies"]:
        book["numCopies"] = int(book["numCopies"]["$numberInt"])

    return book["numCopies"]

# numCopies increment and decrement
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
    
@app.put("/books/decr/{isbn}")
def decr_book_copies(isbn: int):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return JSONResponse(status_code=404, content={"message": "Book on hold is not found"})
    result = db["books"].update_one({"isbn": isbn}, {"$inc": {"numCopies": -1}})

    if result.modified_count > 0:
        return JSONResponse(status_code=200, content={"message": "Copy successfully passed to the next user in the queue!"})
    else:
        return JSONResponse(status_code=500, content={"message": "Failed to update book for reservation."})