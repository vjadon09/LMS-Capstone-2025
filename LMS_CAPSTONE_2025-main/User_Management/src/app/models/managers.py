from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import re
from pymongo import ReturnDocument
from fastapi.responses import JSONResponse

class Manager(BaseModel):
    _id: str
    managerID: str
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    address: Optional[dict]
    passwordHash: str
    
    class Config:
        json_encoders = {ObjectId: str}
    
app = FastAPI()

@app.get("/managers/", response_model=List[Manager])
def list_managers():
    db = get_db()
    managers = db["managers"].find()
    managers_list = []
    for manager in managers:
        manager["_id"] = str(manager["_id"])
        managers_list.append((manager))
    return managers_list

def manager_created_on_date(manager):
    obj_id = ObjectId(manager['_id'])
    created_on = obj_id.generation_time
    return created_on 

def get_manager_metadata(email: str):
    cleaned_email = re.sub(r"[()]", '', email)
    user = db["managers"].find_one({"managerID": cleaned_email})
    if not user:
        return {
            "firstName": "undefined",
            "lastName": "undefined",
            "age": 0,
            "email": "undefined",
            "managerID": "undefined",
            "password": "undefined"
        }

    return {
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
        "age": 0,
        "email": user.get("email"),
        "managerID": user.get("managerID"),
        "password": user.get("passwordHash")
    }
    
def delete_manager(manager_id: str):
    result = db["managers"].delete_one({"managerID": manager_id})
    
    if result.deleted_count > 0:
        return JSONResponse(status_code=200, content={"message": f"Manager with ID {manager_id} was successfully deleted."})
    else:
        return JSONResponse(status_code=409, content={"message": f"No manager found with ID {manager_id}."})

def edit_manager(username: str, first_name: str, last_name: str, email: str, managerID: str):   
    updated_document = db["managers"].find_one_and_update({"managerID": username}, 
        {"$set": {"email":email, "firstName":first_name, "lastName":last_name}}, 
        return_document = ReturnDocument.AFTER)
    if managerID != updated_document["managerID"]:
        print(db["managers"].update_one({"_id":updated_document["_id"]}, {"$set": {"managerID":managerID, "passwordHash":managerID}}))
    return JSONResponse(status_code=200, content={"message": "Manager details updated successfully"})

def add_manager(firstName: str, lastName: str, email: str, password: str, managerID: str):
    existing_manager = db["managers"].find_one({"managerID": managerID})
    if existing_manager:
        return JSONResponse(status_code=409, content={"message": "Manager already exists."})
    
    result = db["managers"].insert_one({"firstName": firstName, "lastName": lastName, "managerID": managerID, "email": email, "password": password})
    if result:
        return JSONResponse(status_code=200, content={"message": "Manager successfully created!"})
    else:
        return JSONResponse(status_code=409, content={"message": "Error creating manager."}) 