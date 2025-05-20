from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from .database.db import *
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument
from fastapi.responses import JSONResponse

app = FastAPI()

class Address(BaseModel):
    streetAddress: str
    city: str
    state: str
    country: str

class Customer(BaseModel):
    _id: str
    email: str
    password: str
    firstName: str
    lastName: str
    address: Address
    age: int
    
    class Config:
        json_encoders = {ObjectId: str}
    
@app.post("/customers/", response_model=dict)
def create_user(customer: Customer):
    customer_dict = customer.dict()
    result = db["customers"].insert_one(customer_dict)
    return {"id": str(result.inserted_id)}

@app.get("/customers/")
def list_users():
    db = get_db()
    customers = db["customers"].find()
    customers_list = []
    for customer in customers:
        customer["_id"] = str(customer["_id"])
        customers_list.append((customer))
    return customers_list

def customer_created_on_date(customer):
    obj_id = ObjectId(customer["_id"])
    created_on = obj_id.generation_time
    return created_on

def get_customer_metadata(email: str):
    user = db["customers"].find_one({"email": email})
    if not user:
        return {
            "firstName": "undefined",
            "lastName": "undefined",
            "age": 0,
            "email": "undefined",
            "password": "undefined"
        }
    return {
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
        "age": user.get("age"),
        "email": user.get("email"),
        "password": user.get("password")
    }
    
def delete_customer(email: str):
    result = db["customers"].delete_one({"email": email})
    if result.deleted_count > 0:
        return JSONResponse(status_code=200, content={"message": f"Customer with email {email} was successfully deleted."})
    else:
        return JSONResponse(status_code=409, content={"message": f"No customer found with email {email}."})

def edit_customer(username: str, first_name: str, last_name: str, age: int, email: str):   
    updated_document = db["customers"].find_one_and_update({"email": username}, 
        {"$set": {"age":age, "firstName":first_name, "lastName":last_name}}, 
        return_document = ReturnDocument.AFTER)
    if email != updated_document["email"]:
        db["customers"].update_one({"_id":updated_document["_id"]}, {"$set": {"email":email}})
    return JSONResponse(status_code=200, content={"message": "Customer details updated successfully"})

def add_customer(firstName: str, lastName: str, age: int, email: str, password: str):
    existing_customer = db["customers"].find_one({"email": email})
    if existing_customer:
        return JSONResponse(status_code=409, content={"message": "Customer with this email already exists."})
    
    result = db["customers"].insert_one({"firstName": firstName, "lastName": lastName, "age": age, "email": email, "password": password})
    if result:
        return JSONResponse(status_code=200, content={"message": "Customer successfully created!"})
    else:
        return JSONResponse(status_code=409, content={"message": "Error creating customer."}) 