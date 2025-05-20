from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from .database.db import *
from typing import List, Optional

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
    wishlist: List[str]
    
@app.get("/wishlist/{email}", response_model=List[str])
def get_wishlist_by_email(email: str):
    customer = db["customers"].find_one({"email": email})
    if customer is None:
        return []
    list = []
    for w in customer["wishlist"]["items"]:
        list.append({"isbn": w})
        
    return list

@app.delete("/wishlist/{email}")
def clear_wishlist(email: str):
    customer = db["customers"].find_one({"email": email})
    if customer is None:
        return {"message": f"Error deleting the wishlist for {email}"}   
    
    db["customers"].update_one({"email": email}, {"$set": {"wishlist.items": []}})
    
    return {"message": f"Wishlist for {email} has been cleared"}

@app.delete("/wishlist/{email}/{isbn}")
def delete_item_from_wishlist(email: str, isbn: str):
    customer = db["customers"].find_one({"email": email})
    
    if customer is None:
        return "Error"
    if isbn not in customer["wishlist"]["items"]:
        return "Error"
    
    db["customers"].update_one({"email": email}, {"$pull": {"wishlist.items": isbn}})
    
    return "Success"
