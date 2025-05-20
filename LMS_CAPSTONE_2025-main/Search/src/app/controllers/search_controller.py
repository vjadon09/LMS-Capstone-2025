from models.books import *
from models.customers import *
from models.filters import *
from models.bookCovers import *
from typing import List

   
# Get Search query
def retrieve_searchQuery_list(query: str) -> List[Book]:
 
    book_by_title = get_books_by_title(query)  # List
    book_by_author = get_books_by_author(query)  # List
    book_by_genre = get_books_by_genre(query)  # List
    book_by_isbn = get_books_by_isbn(query)
    #book_by_publisher = get_books_by_publisher(query)  # List 
    
    # Combine all the lists
    #all_books = book_by_title + book_by_author + book_by_genre + book_by_publisher
    all_books = book_by_title + book_by_author + book_by_genre + book_by_isbn
    # Remove duplicates by creating a set based on a unique identifier (e.g., combination of title and isbn)
    unique_books = {tuple(book.model_dump().items()) for book in all_books}  # Create a set of unique book identifiers
    
    # If you want to convert back to a list of dictionaries:
    search_result = [Book(**dict(book)) for book in unique_books]  # Convert back to Book instances
    
    return search_result
