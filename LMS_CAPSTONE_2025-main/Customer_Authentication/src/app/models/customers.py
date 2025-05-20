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
    
class Wishlist(BaseModel):
    items: List[str]

class Customer(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    address: Address
    age: int
    wishlist: Wishlist

@app.post("/customers/", response_model=dict)
def create_user(customer: Customer):
    customer_dict = customer.dict()
    result = db["customers"].insert_one(customer_dict)
    return {"id": str(result.inserted_id)}

@app.get("/customers/{email}", response_model=Customer)
def get_user(email: str): 
    customer = db["customers"].find_one({"email": email})
    if not customer:
        return None
    customer["_id"] = str(customer["_id"])
    if isinstance(customer["age"], dict) and "$numberInt" in customer["age"]:
        customer["age"] = int(customer["age"]["$numberInt"])

    return Customer(**customer)

@app.get("/customers/{firstName}", response_model=Customer)
async def get_user_by_fname(firstName: str):
    customer = await get_db["customers"].find_one({"firstName": firstName})
    if not customer:
        raise HTTPException(status_code=404, detail="User not found")
    return Customer(**customer)

@app.get("/customers/", response_model=List[Customer])
def list_users():
    db = get_db()
    customers = list(db["customers"].find())
    return [Customer(**customer) for customer in customers]

@app.delete("/customers/{email}")
async def delete_user(email: str):
    result = await get_db.db["customers"].delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

@app.put("/customers/{email}/password", response_model=dict)
def change_password(email: str, new_password: str):
    customer = get_user(email)
    if not customer:
        raise HTTPException(status_code=404, detail="User not found")
    result = db["customers"].update_one(
        {"email": email},
        {"$set": {"password": new_password}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Password update failed")
    return {"message": "Password updated successfully"}


@app.put("/customers/{email}/password", response_model=dict)
def change_password(email: str, new_password: str):
    customer = get_user(email)
    if not customer:
        raise HTTPException(status_code=404, detail="User not found")

    if customer.password == new_password:
        return {"message": "New password must be different from old password"}
    
    result = db["customers"].update_one(
        {"email": email},
        {"$set": {"password": new_password}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Password update failed")
    
    return {"message": "Password updated successfully"}