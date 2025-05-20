from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import field_validator
from fastapi.responses import JSONResponse
import pytz
from models.books import *

app = FastAPI()

class Reservations(BaseModel):
    reservation_id: str
    user_email: str
    book_id: str
    reservation_date: str
    expiration_date: str
    status: str
    isbn: str
    
    @field_validator('reservation_id', mode='before')
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

@app.get("/holds/", response_model=List[Reservations])
def list_holds():
    db = get_db()
    holds = list(db["reservations"].find())
    for hold in holds:
        hold["_id"] = str(hold["_id"]) 
        hold["reservation_id"] = str(hold["reservation_id"]) if isinstance(hold["reservation_id"], ObjectId) else hold["reservation_id"]
    return [Reservations(**hold) for hold in holds]

@app.get("/extendHold/")
def extend_hold(isbn: str, book_id: str):
    reservation = db["reservations"].find_one({"isbn": isbn, "book_id": book_id})
    if not reservation:
        return JSONResponse(status_code=404, content={"message": "Hold not found"})
    
    # Extend the due date by 5 days
    new_due_date = extend_due_date(reservation["expiration_date"])
    if new_due_date is None:
        return JSONResponse(status_code=400, content={"message": "Invalid due date format"})

    update_result = db["reservations"].update_one({"_id": reservation["_id"]}, {"$set": {"expiration_date": new_due_date}})
    if update_result.modified_count == 0:
        return JSONResponse(status_code=500, content={"message": "Failed to update the due date"})
    
    return JSONResponse(status_code=200, content={"message": "Hold successfully extended"})

# Helper function to extend the due date by 5 more days
def extend_due_date(due_date) -> str:
    try:
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        if isinstance(due_date, datetime):
            new_due_date = due_date + timedelta(days=5)
            return new_due_date.isoformat()
        else:
            return None
    except ValueError as e:
        return None
    
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
        if book_response.status_code == 200:
            return True
    else:
        return False    

@app.delete("/delete-reservation/")
def delete_reservation(isbn: str, book_id: str):
    reservation = db["reservations"].find_one({"isbn": isbn, "book_id": book_id})
    if not reservation:
        return JSONResponse(status_code=404, content={"message": "Reservation not found"})
    delete_result = db["reservations"].delete_one({"_id": reservation["_id"]})
    if delete_result.deleted_count == 0:
        return JSONResponse(status_code=500, content={"message": "Failed to delete reservation"})
    
    return JSONResponse(status_code=200, content={"message": "Reservation deleted successfully"})
