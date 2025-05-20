from fastapi import APIRouter, Form, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from controllers.search_controller import *
from controllers.token import *
from models.reviews import *
from models.reservations import *
import os
from io import BytesIO

USER_LOGIN_PAGE = "https://34.47.39.132/auth/login"
USER_LOGOUT_PAGE = "https://34.47.39.132/auth/logout"
MYLIBRARY_PAGE = "https://34.47.39.132/mylib/dashboard"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    user_name = request.cookies.get("user_name", "Guest")
    return templates.TemplateResponse("search_page.html", {"request": request, "name": user_name})

@router.get("/item-info", response_class=HTMLResponse)
def item_info_page(request: Request):
    return templates.TemplateResponse("item_info.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return RedirectResponse(url=USER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    response = RedirectResponse(url=USER_LOGOUT_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("login_token")
    response.delete_cookie("user_name")
    return response

@router.get("/mylib", response_class=HTMLResponse)
def mylibrary_page(request: Request):
    login_token = request.cookies.get("login_token")
    if login_token:
        try:
            verify_jwt(login_token)
            return RedirectResponse(url=MYLIBRARY_PAGE, status_code=status.HTTP_303_SEE_OTHER)
        except HTTPException:
            pass
    return RedirectResponse(url="/search/logout", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/searchQuery", response_class=JSONResponse)
async def search_query_page(request: Request, query: str):
    import re
    query = query.lower().strip()
    query_regex = r'\b' + re.escape(query) + r'\b'  # Using re.escape to handle special characters safely
    results = retrieve_searchQuery_list(query)
    # Filter the results to only include books where the title matches the query exactly
    #filtered_results = [book for book in results if re.search(query_regex, book.title.lower())]

    search_results = [{
        "title": book.title,
        "author":book.author,
        "genre": book.genre,
        "rating": book.rating,
        "kidFriendly": book.kidFriendly,
        "description":  book.description,
        "format": book.format,
        "pageNumber":  book.pageNumber,
        "publisher":  book.publisher,
        "status":  book.status,
        "isbn": book.isbn,
        "numOfMins": book.numOfMins,
        "numCopies": book.numCopies
    } for book in results]

    if not results:
        return JSONResponse(content={"message": "No books found matching your search."}, status_code=status.HTTP_404_NOT_FOUND)
    
    # Return books as JSON data
    return JSONResponse(content={"books": search_results})

@router.get("/popular", response_class=JSONResponse)
async def get_popular_books():
    results = get_popular()
    content = {'titles':[], 'isbns':[]}
    for book in results:
        content["titles"].append(book["title"])
        content["isbns"].append(book["isbn"])
    return JSONResponse(content)

@router.get("/newest", response_class=JSONResponse)
async def get_newest_books():
    results = get_newest()  
    content = {'titles':[], 'isbns':[]}
    for book in results:
        content["titles"].append(book["title"])
        content["isbns"].append(book["isbn"])
    return JSONResponse(content) 

@router.get("/serve-book-cover/{isbn}", response_class=StreamingResponse)
async def serve_cover(isbn: str):
    data = await get_book_cover(isbn)
    file = BytesIO(data)
    response = StreamingResponse(file, media_type="image/jpg")
    return response

@router.get("/search_result_page", response_class=HTMLResponse)
async def get_search_result_page(request: Request, query: str):
    
    # Pass the query to the HTML template (if present)
    print(f'search_result_page query value:',query)
    return templates.TemplateResponse("search_result_page.html", {"request": request, "query": query})
    
    
'''Filtered queries'''
# Define the endpoint to receive filters and return filtered books
@router.post("/filter_books", response_class=JSONResponse)
async def filter_books(filters: FilterRequest):
    
    books = retrieve_searchQuery_list(filters.searchQuery)
    print(filters)
    
    # Filter the books based on the given filters
    filtered_books = [book for book in books if
        (not filters.genres or book.genre in filters.genres) and
        (not filters.formats or book.format in filters.formats) and
        (not filters.availability or 
            (("Available" in filters.availability and book.status == "Available"))) and
        (not filters.audience or 
            (("True" in filters.audience and book.kidFriendly) or  # kidFriendly = True
            ("False" in filters.audience and not book.kidFriendly))) and  # kidFriendly = False
        (not filters.ratings or round(book.rating) in filters.ratings)
        ]

    # If no books match the filters, return an empty list
    if not filtered_books:
        return JSONResponse(content=[], status_code=200)

    # Convert the filtered books to a dictionary that can be returned as JSON
    books_list = [{
        "title": book.title,
        "author":book.author,
        "genre": book.genre,
        "rating": book.rating,
        "kidFriendly": book.kidFriendly,
        "description":  book.description,
        "format": book.format,
        "pageNumber":  book.pageNumber,
        "publisher":  book.publisher,
        "status":  book.status,
        "isbn": book.isbn,
        "numOfMins": book.numOfMins,
        "numCopies": book.numCopies
    } for book in filtered_books]

    # Return the filtered books as a JSONResponse
    return JSONResponse(content=books_list, status_code=200)


@router.get("/book_info/{isbn}")
async def get_book_info(isbn: str):
    book_info = get_book(isbn)
    if isinstance(book_info, Book):  
        book_info = book_info.model_dump()  
    return book_info


@router.get("/book_info", response_class=HTMLResponse)
async def get_book_info_page(request: Request, isbn: str):
    # Pass the query to the HTML template (if present)
    print(f'isbn from book_info', isbn)
    return templates.TemplateResponse("item_info.html", {"request": request, "isbn": isbn})


# place an item on hold
@router.post("/place_hold/{isbn}")
async def place_hold(request: Request, isbn: str):
    is_available = get_book_status(isbn)
    
    # check if the user already has a hold for the same item
    email_token = request.cookies.get("login_token")
    if not email_token:
        return JSONResponse(content={"message": "Unable to place a hold. Please login again."}, status_code=status.HTTP_400_BAD_REQUEST)
    email = verify_jwt(email_token)
    is_non_duplicate_hold = get_non_duplidate_hold_status(isbn, email["subject"])
    
    if is_non_duplicate_hold == False:
        return JSONResponse(content={"message": "A hold has already been placed on this book under your account."}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # Otherwise add the user to the queue
    if is_available:
        response = add_user_to_queue(isbn, request)  # add user to queue
        if response:
            response2 = decr_book_copies(isbn)
            if response2:
                return JSONResponse(content={"message": "Hold placed successfully!"}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": "Error placing a hold"}, status_code=status.HTTP_409_CONFLICT)
    else:
        return JSONResponse(content={"message": "Book unavailable. Add to your wishlist for availability updates!"}, status_code=status.HTTP_400_BAD_REQUEST)    

@router.get("/review-reservations")
def review_reservations():
    return_expired_books()
    response = update_all_statuses()
    if response:
        return JSONResponse(content={"message": "Existing holds updated."}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={"message": "No holds to update."}, status_code=status.HTTP_200_OK)


# add to wishlist
@router.post("/add-to-wishlist")
async def add_to_wishlist(request: Request):
    login_token = request.cookies.get("login_token")
    user_email = verify_jwt(login_token)["subject"]
    body = await request.json()
    isbn = body.get("isbn")
    return update_user_wishlist(user_email, isbn)


# write a review
@router.post("/write-review")
async def write_review(
    request: Request,
    rating: int = Form(...),
    review_comment: str = Form(...),
    isbn: str = Form(...)
)->None:
    print(f'received review from router {review_comment}')
    await add_review(request, rating, review_comment, isbn )


# retrieve review from db
@router.get("/retrieve-reviews")
async def get_reviews(request: Request, isbn: str):
    # given isbn, return a list of reviews with 'username, rating, review'
    reviews_list=get_reviews_db(isbn)
    return {"reviews":reviews_list }


# join queue
@router.post("/join_queue")
# should also expxect username as a field in the following async method
async def join_queue(request: Request ):
    
    '''
    - receive a user
    - add this user to the queue database with associated book isbn
    - give it a queue_status number in the queue 
    '''
    
    return ""