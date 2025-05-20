from fastapi import FastAPI
from pydantic import BaseModel
from .database.db import *
from typing import List
from fastapi.responses import StreamingResponse
import gridfs
from io import BytesIO

app = FastAPI()

class digitalMaterial(BaseModel):
    isbn: str
    file: bytes
    
@app.get("/epubs")
async def get_book_epub(isbn: str):
    epub = db["digitalMaterial"].find_one({"isbn": isbn})
    return epub["file"]

@app.get("/audiobooks")
async def get_book_audio(isbn: str):
    audio = db["digitalMaterial"].find_one({"isbn": isbn})
    return audio["file"]
    