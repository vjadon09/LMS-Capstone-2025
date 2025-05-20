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
@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    book = db["books"].find_one({"isbn": isbn})
    if not book:
        return None
    book["_id"] = str(book["_id"])

    if isinstance(book["pageNumber"], dict) and "$numberInt" in book["pageNumber"]:
        book["pageNumber"] = int(book["pageNumber"]["$numberInt"])
    if isinstance(book["numCopies"], dict) and "$numberInt" in book["numCopies"]:
        book["numCopies"] = int(book["numCopies"]["$numberInt"])
    if isinstance(book["numOfMins"], dict) and "$numberInt" in book["numOfMins"]:
        book["numOfMins"] = int(book["numOfMins"]["$numberInt"])
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

# Delete entire book
@app.delete("/books/{isbn}", response_model=dict)
def delete_book(isbn: str):
    result = db["books"].delete_one({"isbn": isbn})
    if result.deleted_count > 0:
        return {"message": "Book deleted successfully."}
    else:
        return {"message": "Error deleting book."}
    
    
# Update book fields
@app.put("/catalog/update-isbn/{isbn}", response_model=dict)
def update_isbn(isbn: str, new_isbn: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"isbn": new_isbn}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-title/{isbn}", response_model=dict)
def update_title(isbn: str, new_title: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"title": new_title}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-description/{isbn}", response_model=dict)
def update_description(isbn: str, new_description: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"description": new_description}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-numCopies/{isbn}", response_model=dict)
def update_numCopies(isbn: str, new_copies: float):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"numCopies": new_copies}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-author/{isbn}", response_model=dict)
def update_author(isbn: str, new_author: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"author": new_author}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-genre/{isbn}", response_model=dict)
def update_genre(isbn: str, new_genre: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"genre": new_genre}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-kidFriendly/{isbn}", response_model=dict)
def update_kidFriendly(isbn: str, new_kidFriendly: bool):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"kidFriendly": new_kidFriendly}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-format/{isbn}", response_model=dict)
def update_format(isbn: str, new_format: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"format": new_format}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-pageNumber/{isbn}", response_model=dict)
def update_pageNumber(isbn: str, new_pageNumber: int):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"pageNumber": new_pageNumber}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-numOfMins/{isbn}", response_model=dict)
def update_numOfMins(isbn: str, new_numOfMins: int):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"numOfMins": new_numOfMins}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-publisher/{isbn}", response_model=dict)
def update_publisher(isbn: str, new_publisher: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"publisher": new_publisher}}
    )
    return result.modified_count > 0

@app.put("/catalog/update-status/{isbn}", response_model=dict)
def update_status(isbn: str, new_status: str):
    result = db["books"].update_one(
        {"isbn": isbn},
        {"$set": {"status": new_status}}
    )
    return result.modified_count > 0