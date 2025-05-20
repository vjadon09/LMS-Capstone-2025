from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .database.db import *
from pymongo import MongoClient

class Manager(BaseModel):
    managerID: str
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    address: Optional[dict]
    passwordHash: str

    class Config:
        orm_mode = True

app = FastAPI()

@app.get("/managers/{managerID}", response_model=Manager)
def get_manager(managerID: str):
    manager = db["managers"].find_one({"managerID": managerID})
    if not manager:
        return None
    manager["_id"] = str(manager["_id"])
    
    return Manager(**manager)

# manager and user should not have the email address
@app.get("/managers/{email}", response_model=Manager)
def get_manager_by_email(email: str):
    manager = db["managers"].find_one({"email": email})
    if not manager:
        return None
    manager["_id"] = str(manager["_id"])
    
    return Manager(**manager)