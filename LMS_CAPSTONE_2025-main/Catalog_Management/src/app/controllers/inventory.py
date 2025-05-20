from controllers.token import *
from models.books import *
from models.bookCovers import *
from models.digitalMaterial import *

def handle_add_book(title: str, isbn: str, author: str, genre: str, rating: float,
                    kidFriendly: bool, description: str, format: str, pageNumber: int, 
                    numCopies: int, numOfMins: int, publisher: str, status: str, image: str, content: str):
    # Check if book isbn is already in the database
    book = get_book(isbn)
    
    if book is None:
        response1 = create_book(Book(title=title, isbn=isbn, author=author, genre=genre, rating=rating,
            kidFriendly=kidFriendly, description=description, format=format, pageNumber=pageNumber, 
            numCopies=numCopies, numOfMins=numOfMins, publisher=publisher, status=status))
        
        # Check if image is uploaded
        if image is not None:
            response2 = add_book_cover(isbn, image)
            
            # Check if book content is uploaded
            if content is not None:
                response3 = add_book_file(isbn, content)
                
        else:
            response2 = "Error"
    else:
        response1 = "Error"
        response2 = "Error"
        response3 = "Error"
        
    if response1=="Error" or response2=="Error" or response3=="Error":
        return "Error"
    else:
        return response2

def handle_modify_book(title: str, isbn: str, author: str, genre: str, numCopies: int, description: str, kidFriendly: bool, format: str, pageNumber: int, numOfMins: int, publisher: str, status: str, file: str, image: str):
    book = get_book(isbn)

    if book is not None:
        updates = {"title": title, "isbn": isbn, "author": author, "genre": genre, "numCopies": numCopies,
                    "description": description, "kidFriendly": kidFriendly, "format": format, "pageNumber": pageNumber, "numOfMins": numOfMins,
                    "publisher": publisher, "status": status}
        update_occurred = False
        
        for field, new in updates.items():
            if getattr(book, field) != new:
                update_method = globals().get(f"update_{field}")
                if update_method:
                    response = update_method(book.isbn, new)
                    print(f"\n\n{response}\n\n")
                    if response:
                        update_occurred = True
        if image is not None:
            update_occurred = modify_book_cover(isbn, image)
        if file is not None:
            update_occurred = modify_book_file(isbn, file)
        return update_occurred
        
    return False