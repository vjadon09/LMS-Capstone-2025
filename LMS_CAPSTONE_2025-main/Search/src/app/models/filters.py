from pydantic import BaseModel
from typing import List, Optional


# Define the filter query parameters as a model
class FilterRequest(BaseModel):
    searchQuery: str
    genres: List[str]
    formats: List[str]
    availability: List[str]
    audience: List[str]
    ratings: List[float] 
