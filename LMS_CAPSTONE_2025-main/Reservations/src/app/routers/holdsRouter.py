from fastapi import APIRouter, Body, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from controllers.token import *
from controllers.holds import *
import os

MANAGER_LOGIN_PAGE = "https://34.47.39.132/auth/manager"
ADMIN_DASHBOARD_PAGE = "https://34.47.39.132/catalog/admin_dashboard"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/manager-login", response_class=HTMLResponse)
def manager_login_page(response: Response):
    response = RedirectResponse(url=MANAGER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("manager_login_token")
    response.delete_cookie("manager_name")
    return response

@router.get("/holds-admin", response_class=HTMLResponse)
def holds_admin_page(request: Request):
    return templates.TemplateResponse("manage_holds_admin.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(response: Response):
    response = RedirectResponse(url=ADMIN_DASHBOARD_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.post("/dashboard", response_class=HTMLResponse)
async def dashboard(response: Response):
    response = RedirectResponse(url=ADMIN_DASHBOARD_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

# Filling the table in Manage Holds page
@router.get("/list-holds/", response_model=List[Reservations])
def list_holds_json():
    holds = list_holds()
    return JSONResponse(content=[hold.dict() for hold in holds])

# Getting the book title from the database
@router.get("/book-title/{isbn}", response_model=dict)
def book_title_json(isbn: str):
    title = get_book_title(isbn)
    if title == "Book not found":
        return JSONResponse(status_code=404, content={"message": title})
    return JSONResponse(content={"title": title})

# Extending the hold by 5 days in the database
@router.post("/extend-hold/{isbn}/{book_id}")
def extend_hold_json(isbn: str, book_id: str):
    return extend_hold(isbn, book_id)

# Updating the status of the reservations
@router.get("/update-status/{isbn}/{book_id}")
async def update_status(isbn: str, book_id: str):
    reservations_count_waiting = db["reservations"].count_documents({"isbn": isbn, "status": "pending"})
    copies = get_book_copies(isbn)
    print(f"\n{reservations_count_waiting} || {copies} || {isbn}, {book_id}\n")
    response = False
    if copies >= 1 and reservations_count_waiting > 0:
        response = update_hold_status(isbn, book_id)
    
    if response:
        return JSONResponse(status_code=200, content={"message": f"Status updated {isbn} | {book_id}."})
    return JSONResponse(status_code=200, content={"message": f"Status not updated {isbn} | {book_id}."})

@router.post("/delete-hold/{isbn}/{book_id}")
async def delete_hold_json(isbn: str, book_id: str):
    response1 = delete_reservation(isbn, book_id)
    if response1.status_code == 200:
        response2 = incr_book_copies(isbn)
        return response2
    else:
        return response1