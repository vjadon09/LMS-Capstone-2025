from models.books import *


def get_availability(status: str)->List[Book]:
    
    return get_books_by_status(status)


def get_genre(genre: str)->List[Book]:
    
    return get_books_by_genre(genre)


def get_rating(rating: float)->List[Book]:
    
    return get_books_by_rating(rating)