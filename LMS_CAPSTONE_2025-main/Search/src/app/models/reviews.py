from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
import jwt
from pydantic import BaseModel
from datetime import datetime
from controllers.token import SECRET_KEY
from .database.db import db

app = FastAPI()

class Review(BaseModel):
    book_id: str
    review_text: str
    rating: float

@app.post("/write-review")
async def add_review(request: Request, rating: int, review_comment: str, isbn: str)-> None:
    print("received review from db!")
    # Securely get user info from session
    token = request.cookies.get("login_token")
    
    if not token:
        return {"message": "Your session has expired. Please login again."}
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload.get("sub")
    
    if not email:
        return {"message": "Invalid session."}

    review_data = {
        "user_email": email,
        "book_id": isbn,
        "review_text": review_comment,
        "created_at": datetime.utcnow(),
        "rating": float(rating)
    }

    # add to databse
    db["reviews"].insert_one(review_data)
    print(f'added {review_comment} to db!')


# get reviews from db
@app.get("/reviews/{isbn}", response_model=list[dict])
def get_reviews_db(isbn: str):
    reviews_cursor = db["reviews"].find({"book_id": isbn})
    reviews_list = []

    for review in reviews_cursor:
        user_email = review.get("user_email")
        user = db["customers"].find_one({"email": user_email}, {"firstName": 1, "lastName": 1})
        try:
          reviews_list.append({
              "user": review.get("user_email").split('@')[0],  # just the username part
              "firstName" : user.get("firstName"),
              "lastName" : user.get("lastName"),
              "rating": review.get("rating"),
              "review_text": review.get("review_text"),
              "created_at": review.get("created_at").strftime("%Y-%m-%d")
          })
        except AttributeError:
          print("Customer does not exist")
    return reviews_list