from fastapi import APIRouter, Body, status, Request, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, Response, JSONResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from controllers.token import *
from controllers.inventory import *
from datetime import datetime
import os, base64
from io import BytesIO

MANAGER_LOGIN_PAGE = "https://34.47.39.132/auth/manager"
MANAGE_HOLDS_ADMIN = "https://34.47.39.132/reservations/holds-admin"
USER_MANAGEMENT_PAGE = "https://34.47.39.132/userManage/main"
NOTIFICATIONS_PAGE = "https://34.47.39.132/notif/main"
USER_LOGIN_PAGE = "https://34.47.39.132/auth/login"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/edit_inventory", response_class=HTMLResponse)
def edit_inventory_page(request: Request):
    return templates.TemplateResponse("edit_inventory.html", {"request": request})

@router.get("/admin_dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    manager_name = request.cookies.get("manager_name", "Admin")
    curHr = datetime.now().hour
    # Determine greeting
    if 0 <= curHr < 12:
        greeting = f"Good Morning {manager_name} 🖥️"
    elif 12 <= curHr < 17:
        greeting = f"Good Afternoon {manager_name} 🖥️"
    else:
        greeting = f"Good Evening {manager_name} 🖥️"
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "greeting": greeting})

@router.get("/manager-login", response_class=HTMLResponse)
def manager_login_page(response: Response):
    response = RedirectResponse(url=MANAGER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("manager_login_token")
    response.delete_cookie("manager_name")
    return response

# Manage holds page button

@router.get("/manage-holds", response_class=HTMLResponse)
def manage_holds_page(response: Response):
    return RedirectResponse(url=MANAGE_HOLDS_ADMIN, status_code=status.HTTP_303_SEE_OTHER)

# View Inventory page button
@router.get("/view-inventory", response_class=HTMLResponse)
def view_inventory_page(request: Request):
    return templates.TemplateResponse("view_inventory.html", {"request": request})

# View User Management page button
@router.get("/userManage", response_class=HTMLResponse)
def view_inventory_page(request: Request):
    return RedirectResponse(url=USER_MANAGEMENT_PAGE, status_code=status.HTTP_303_SEE_OTHER)

# View notification management page button
@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(request: Request):
    return RedirectResponse(url=NOTIFICATIONS_PAGE, status_code=status.HTTP_303_SEE_OTHER)

# Redirect to the customer auth page
@router.get("/loginCustomer", response_class=HTMLResponse)
def view_login_customer(request: Request):
    return RedirectResponse(url=USER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)

# Edit inventory page buttons (x3)
@router.get("/add-item", response_class=HTMLResponse)
def add_item_page(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})

@router.post("/add-item", response_class=HTMLResponse)
async def add_item(title: str = Body(...), isbn: str = Body(...), author: str = Body(...), genre: str = Body(...), rating: float = Body(...),
            kidFriendly: bool = Body(...), description: str = Body(...), format: str = Body(...), pageNumber: int = Body(...), 
            numCopies: int = Body(...), numOfMins: int = Body(...), publisher: str = Body(...), status: str = Body(...) ,
            imageUpload: UploadFile = File(...), bookFile: UploadFile = File(...)):
    if imageUpload:
        image_data = await imageUpload.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        if bookFile:
            file_data = await bookFile.read()
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            result = result = handle_add_book(title, isbn, author, genre, rating, kidFriendly, description, format, pageNumber, numCopies, numOfMins, publisher, status, image_base64, file_base64)
        else:
            result = handle_add_book(title, isbn, author, genre, rating, kidFriendly, description, format, pageNumber, numCopies, numOfMins, publisher, status, image_base64, None)
    else:
        result = handle_add_book(title, isbn, author, genre, rating, kidFriendly, description, format, pageNumber, numCopies, numOfMins, publisher, status, None, None)
        
    if result == "Error":
        return JSONResponse(status_code=409, content={"detail": "Item already exists."})
    return RedirectResponse(url="/catalog/edit_inventory", status_code=303)

@router.get("/remove-item", response_class=HTMLResponse)
def remove_item_page(request: Request):
    books = list_books()
    return templates.TemplateResponse("delete_book.html", {"request": request, "books": books})

@router.get("/books/", response_model=List[Book])
def list_books_json():
    books = list_books()
    return JSONResponse(content=[book.dict() for book in books])

@router.get("/delete-books/{isbn}")
def delete_book_request(isbn: str):
    book_result = delete_book(isbn)
    cover_result = delete_book_cover(isbn)
    file_result = delete_book_file(isbn)
    
    if book_result["message"] == "Error deleting book.":
        return JSONResponse(status_code=409, content=book_result)
    if cover_result["message"] == "Error deleting book cover.":
        return JSONResponse(status_code=409, content=cover_result)
    if file_result["message"] == "Error deleting book file.":
        return JSONResponse(status_code=409, content=cover_result)
    
    return JSONResponse(status_code=200, content={"message": "Book metadata, file, and cover deleted successfully."})

@router.get("/modify-item", response_class=HTMLResponse)
def modify_item_page(request: Request):
    return templates.TemplateResponse("modify_book.html", {"request": request})

@router.post("/modify-item", response_class=HTMLResponse)
async def modify_item(title: str = Body(...), isbn: str = Body(...), author: str = Body(...), genre: str = Body(...),
                numCopies: int = Body(...), description: str = Body(...),
                format: str = Body(...), pageNumber: int = Body(...), numOfMins: int = Body(...), publisher: str = Body(...), status: str = Body(...), bookFile: UploadFile = File(...), imageUpload: UploadFile = File(...), kidFriendly: bool = Body(...)):
    image_base64 = None
    file_base64 = None

    if (imageUpload.content_type.startswith('image/')):
        image_data = await imageUpload.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    if bookFile.filename != "":
        file_data = await bookFile.read()
        file_base64 = base64.b64encode(file_data).decode('utf-8')
    
    result = handle_modify_book(title, isbn, author, genre, numCopies, description, kidFriendly, format, pageNumber, numOfMins, publisher, status, file_base64, image_base64)
    
    if result == False:
        return JSONResponse(
            status_code=409,
            content={"detail": "Nothing has been updated."}
        )
    return RedirectResponse(url="/catalog/edit_inventory", status_code=200)

# Routes to handle book covers 
@router.get("/serve-book-cover/{isbn}", response_class=StreamingResponse)
async def serve_cover(isbn: str):
    data = await get_book_cover(isbn)
    file = BytesIO(data)
    response = StreamingResponse(file, media_type="image/jpg")
    return response

# Route for digital content
@router.get("/file/{isbn}/{format}", response_class=StreamingResponse)
async def serve_file(isbn: str, format:str):
    data = await get_book_file(isbn)
    file = BytesIO(data)
    if format == "eBook":
        media_type_field = "application/epub+zip"
    else:
        media_type_field = "audio/mp3"
    response = StreamingResponse(file, media_type= media_type_field, headers={"Content-Disposition": f"attachment"})
    return response