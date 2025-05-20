from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *
from typing import List
from datetime import datetime
from bson import ObjectId
from pydantic import field_validator
from fastapi.responses import JSONResponse

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

@app.get("/reservations/completed", response_model=List[Reservations])
def get_completed_reservations(email: str):
    current_date = datetime.utcnow()

    completed_reservations = db["reservations"].find({"user_email": email, "status": "complete"})
    
    # {ISBN, Days left, Due Date}
    reservations_data = []
    for r in completed_reservations:
        expiration_date = r["expiration_date"]
        current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        expiration_date = r["expiration_date"].replace(hour=0, minute=0, second=0, microsecond=0)
        
        days_left = (expiration_date - current_date).days
        if days_left < 0:
            db["reservations"].update_one({"isbn": r["isbn"]}, {"$set": {"status": "no longer valid"}})
        else:
            reservations_data.append({"isbn": r["isbn"], "daysLeft": days_left, "expirationDate": r["expiration_date"].isoformat()})
    return reservations_data

@app.get("/reservations/pending", response_model=List[Reservations])
def get_pending_reservations(email: str):

    pending_reservations = db["reservations"].find({"user_email": email, "status": "pending"})
    
    # {ISBN, Queue position, Hold Date}
    reservations_data = []
    
    for r in pending_reservations:        
        existing_holds = list(db["reservations"].find({"isbn": r["isbn"], "status": {'$in': ['pending', 'complete']}}))
        queue = 0
        if len(existing_holds) == 1:
            db['reservations'].update_one({"isbn": r['isbn']},{"$set": {"status": "complete"}})
            return reservations_data
    
        for h in existing_holds:
            if r["book_id"] == h["book_id"]:
                break
            queue += 1
        reservations_data.append({"isbn": r["isbn"], "queue": queue, "reservationDate": r["reservation_date"].isoformat()})
    
    return reservations_data