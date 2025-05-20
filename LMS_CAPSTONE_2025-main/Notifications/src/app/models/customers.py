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
    
def get_user_firstName(email: str):
    customer = db["customers"].find_one({"email": email})
    if not customer:
        return ""
    return customer["firstName"]

def get_user_lastName(email: str):
    customer = db["customers"].find_one({"email": email})
    if not customer:
        return ""
    return customer["lastName"]