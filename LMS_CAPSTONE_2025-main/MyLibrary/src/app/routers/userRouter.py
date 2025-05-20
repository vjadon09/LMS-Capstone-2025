from fastapi import APIRouter, Body, status, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from controllers.token import *
from controllers.mylib import *
import os, base64
from io import BytesIO
import tempfile

USER_LOGIN_PAGE = "https://34.47.39.132/auth/login"
USER_SEARCH_PAGE = "https://34.47.39.132/search/home"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    response = RedirectResponse(url=USER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("login_token")
    response.delete_cookie("user_name")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    name = request.cookies.get('user_name')
    return templates.TemplateResponse("myLibrary.html", {"request": request, "name": name})

@router.get("/access/{isbn}")
async def read_book_page(request: Request, isbn: str):
    title = get_book_by_isbn(isbn)
    format = get_book_format_by_isbn(isbn)
    if format == "eBook":
        epub_url = f"/mylib/epub/{isbn}"
        return templates.TemplateResponse("read_book.html", {"request": request, "title": title, "epub_url": epub_url})
    elif format == "Audio":
        audio_url = f"/mylib/audio/{isbn}"
        return templates.TemplateResponse("listen_book.html", {"request": request, "title": title, "audio_url": audio_url})
    else:
        epub_url = ""
        return templates.TemplateResponse("myLibrary.html", {"request": request})

@router.get("/epub/{isbn}", response_class=StreamingResponse)
async def serve_epub(isbn: str):
    epub_data = await get_book_epub(isbn)
    epub_file = BytesIO(epub_data)
    response = StreamingResponse(epub_file, media_type="application/epub+zip", headers={"Content-Disposition": f"attachment"})
    return response

@router.get("/audio/{isbn}", response_class=FileResponse)
async def serve_audio(isbn: str):
    audio_data = await get_book_audio(isbn)
    audio_file = BytesIO(audio_data)
    response = StreamingResponse(audio_file, media_type="audio/mp3", headers={"Content-Disposition": f"attachment"})
    return response

@router.get("/search", response_class=HTMLResponse)
async def search_page():
    return RedirectResponse(url=USER_SEARCH_PAGE, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/completed-holds")
async def completed_holds(request: Request):
    email = get_user_email_from_token(request.cookies.get("login_token"))
    book_holds = get_completed_reservations(email)
    
    for hold in book_holds:
        temp_title = get_book_by_isbn(hold["isbn"])
        temp_format = get_book_format_by_isbn(hold["isbn"])
        hold["title"] = temp_title
        hold["format"] = temp_format
    
    return book_holds   # {ISBN, Days left, due Date, book title, book format}

@router.post("/pending-holds")
async def pending_holds(request: Request):
    email = get_user_email_from_token(request.cookies.get("login_token"))
    book_holds = get_pending_reservations(email)
    
    for hold in book_holds:
        temp_title = get_book_by_isbn(hold["isbn"])
        hold["title"] = temp_title
    
    return book_holds   # {ISBN, Queue, Hold Date, book title}

@router.post("/wishlist")
async def get_wishlist(request: Request):
    email = get_user_email_from_token(request.cookies.get("login_token"))
    wishlist = get_wishlist_by_email(email)
    for dict in wishlist:
        temp_title = get_book_by_isbn(dict["isbn"])
        dict["title"] = temp_title
    return wishlist

@router.get("/wishlist/clear")
async def reset_wishlist(request: Request):
    email = get_user_email_from_token(request.cookies.get("login_token"))
    return clear_wishlist(email)

@router.get("/wishlist/remove/{items}")
async def wishlist_remove_items(request: Request, items: str):
    email = get_user_email_from_token(request.cookies.get("login_token"))
    items_list = items.split(",")
    for i in items_list:
        msg = delete_item_from_wishlist(email, i)
        if msg == "Error":
            return {"message": "Error deleting books from your wishlist"}
    return {"message": "Successfully deleted books from your wishlist"} 