from datetime import datetime, timedelta
import uuid
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
import jwt
from pydantic import BaseModel, field_validator
from controllers.token import SECRET_KEY
from .database.db import *
import random
import pytz
from models.books import *
import secrets

app = FastAPI()
db = get_db()


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
 
 
 
@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str):
    book_data = db["books"].find_one({"isbn": isbn})
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(**normalize_bson(book_data))


@app.get("/books/{isbn}")
def get_book_status(isbn:str):
    # Fetch the book from the database
    book_data = db["books"].find_one({"isbn": isbn})
    book = normalize_bson(book_data)

    status = book["status"] == "Available"
    print(f'status of book from db {status}')
    return status  # Returns True if available, False otherwise


@app.post("/add_to_queue")
def add_user_to_queue(isbn: str, request: Request):
    # Securely get user info from session
    token = request.cookies.get("login_token")
    if not token:
        return {"message": "Your session has expired. Please login again."}
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_email = payload.get("sub")
    if not user_email:
        return {"message": "Invalid session."}
    
    reservation_date = datetime.utcnow()
    expiration_date = reservation_date + timedelta(days=5)
    
    # No copies available, add to queue
    reservation = {
        "book_id": generate_book_id(isbn),  
        "user_email": user_email,
        "isbn": isbn,
        "reservation_date": reservation_date,
        "expiration_date": expiration_date,
        "status": "pending",
        "reservation_id": generate_random_id()
    }
    
    result = db["reservations"].insert_one(reservation)
    if result.inserted_id:
        return True
    else:
        return False

def generate_random_id(length=24):
    return ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length))
    
def generate_book_id(isbn):
    book = db["books"].find_one({"isbn": isbn})
    title = book['title']
    capital_letters = ''.join([char for char in title if char.isupper()])
    
    def generate_unique_book_id():
        random_number = random.randint(100, 999)
        book_id = f"{capital_letters}-{random_number}"
        if db["reservations"].find_one({"book_id": book_id}):
            return generate_unique_book_id()
        return book_id
    
    return generate_unique_book_id()


@app.get("/return_expired_books")
def return_expired_books():
    local_tz = pytz.timezone("America/New_York")
    today_date = datetime.now(local_tz).date()

    expired_reservations = db["reservations"].find({"status": "complete"})

    for reservation in expired_reservations:
        expiration_date = reservation.get("expiration_date")

        if isinstance(expiration_date, str):
            expiration_date = datetime.fromisoformat(expiration_date)

        if expiration_date.date() < today_date:
            incr_book_copies(reservation["isbn"])
            db["reservations"].delete_one({"_id": reservation["_id"]})

    return True


def update_hold_status(isbn: str, book_id: str):
    local_tz = pytz.timezone("America/New_York") 
    today_date = datetime.now(local_tz)
    hold = db["reservations"].find_one({"isbn": isbn, "book_id": book_id})
    
    reservation_date = hold.get("reservation_date")
    expiration_date = hold.get("expiration_date")

    if isinstance(reservation_date, str):
        reservation_date = datetime.fromisoformat(reservation_date)
    if isinstance(expiration_date, str):
        expiration_date = datetime.fromisoformat(expiration_date)
    
    update_result = None
    if (reservation_date.date() == today_date.date()) or ((today_date.date() > reservation_date.date()) and (today_date.date() <= expiration_date.date())):
        new_status = "complete"
        update_result = db["reservations"].update_one({"_id": hold["_id"]}, {"$set": {"status": new_status}})
        
    if update_result and update_result.modified_count > 0:
        book_response = decr_book_copies(isbn)
        if book_response:
            return True
    else:
        return False    
    
def update_all_statuses():
    reservations = db["reservations"].find({"status": "pending"})
    
    updated_reservations = []
    for reservation in reservations:
        isbn = reservation["isbn"]
        book_id = reservation["book_id"]
        waiting = db["reservations"].count_documents({"isbn": isbn, "status": "pending"})
        copies = get_book_copies(isbn)
        
        if copies >= 1 and waiting > 0:
            response = update_hold_status(isbn, book_id)
            if response:
                updated_reservations.append(book_id)
    if updated_reservations:
        return True
    return False

def get_non_duplidate_hold_status(isbn, email):
    reservation = db["reservations"].find_one({"isbn": isbn, "user_email": email})
    return reservation is None