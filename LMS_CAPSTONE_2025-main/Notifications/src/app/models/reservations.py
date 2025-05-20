from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import field_validator
from fastapi.responses import JSONResponse
import pytz

app = FastAPI()

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
    
@app.get("/get-recently-available")    
def get_recently_available():
    holds = list(db.reservations.find(
        { "status": "no longer valid" },
        { "isbn": 1, "_id": 0 }))
    
    return holds[::-1]    # returns a list of ISBNs of recently available books

@app.get("/get-waiting-users")
def get_waiting_users():
    users = list(db.reservations.find(
        { "status": "pending" },
        { "user_email": 1, "isbn": 1, "_id": 0 }))
    
    return users[::-1]    # returns a list of ISBNs and use emails of waiting users

@app.get("/get-due-today")
def get_due_today():
    today_start = datetime.combine(datetime.today().date(), datetime.min.time())
    today_end = today_start + timedelta(days=1) - timedelta(seconds=1)
    
    holds = list(db.reservations.find(
        { "status": "complete", "expiration_date": { "$gte": today_start, "$lte": today_end } },
        { "user_email": 1, "isbn": 1, "book_id": 1, "_id": 0 }
    ).sort("expiration_date", -1))

    return holds    # returns a list of holds that are due today

@app.get("/get-due-soon")
def get_due_soon():
    today_start = datetime.combine(datetime.today().date(), datetime.min.time()) + timedelta(days=1)
    three_days_later = today_start + timedelta(days=3)
    
    holds = list(db.reservations.find(
        { "status": "complete", "expiration_date": { "$gte": today_start, "$lte": three_days_later }},
        { "user_email": 1, "isbn": 1, "book_id": 1, "expiration_date": 1, "_id": 0 }
    ).sort("expiration_date", 1))

    return holds    # returns a list of holds that are due within 3 days