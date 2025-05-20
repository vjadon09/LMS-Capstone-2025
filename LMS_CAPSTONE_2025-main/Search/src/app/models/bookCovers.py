from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *

app = FastAPI()

class BookCovers(BaseModel):
    isbn: str
    imageURL: bytes
    
@app.get("/book-cover")
async def get_book_cover(isbn: str):
    cover = db["bookCovers"].find_one({"isbn": isbn})
    return cover["imageURL"]