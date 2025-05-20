from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *

app = FastAPI()

class Address(BaseModel):
    streetAddress: str
    city: str
    state: str
    country: str

class Customer(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    address: Address
    age: int

@app.get("/wishlist", response_model=dict)
def update_user_wishlist(email: str, isbn: str):
    user = db["customers"].find_one({"email": email})
    if not user:
        return {"message": "Error finding account! Please login again."}
    
    wishlist = user.get("wishlist", {})
    items = wishlist.get("items", [])
    if isbn in items:
        return {"message": "Book is already in the wishlist!"}
    
    result = db["customers"].update_one({"email": email}, {"$push": {"wishlist.items": isbn}})
    if result.modified_count == 0:
        return {"message": "Error adding book to wishlist!"}
    else:
        return {"message": "Book successfully added to wishlist!"}