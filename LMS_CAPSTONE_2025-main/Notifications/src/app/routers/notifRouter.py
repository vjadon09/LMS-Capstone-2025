from fastapi import APIRouter, Body, status, Request, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, Response, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from controllers.token import *
from controllers.notifications import *
from datetime import datetime
import os, base64, json
from io import BytesIO

MANAGER_LOGIN_PAGE = "https://34.47.39.132/auth/manager"
ADMIN_DASHBOARD_PAGE = "https://34.47.39.132/catalog/admin_dashboard"
MANAGER_CATALOG_PAGE = "https://34.47.39.132/catalog/view-inventory"
USER_MANAGEMENT_PAGE = "https://34.47.39.132/userManage/"

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

@router.get("/admin_dashboard", response_class=HTMLResponse)
def admin_dashboard_page(response: Response):
    return RedirectResponse(url=ADMIN_DASHBOARD_PAGE, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/catalog", response_class=HTMLResponse)
def catalog_page(response: Response):
    response = RedirectResponse(url=MANAGER_CATALOG_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.get("/userManage", response_class=HTMLResponse)
def userManage_page(response: Response):
    response = RedirectResponse(url=USER_MANAGEMENT_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.get("/main", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("notification_center.html", {"request": request})

@router.get("/available-now")
def available_now(request: Request):
    result = handle_get_available_books()
    return result

@router.get("/returns-today")
def return_today(request: Request):
    result = handle_return_books_today()
    return result

@router.get("/return-soon")
def return_soon(request: Request):
    result = handle_return_books_soon()
    return result

@router.post("/send/{tableType}")
async def return_today_email(request: Request, tableType: str):
    body = await request.body()
    data = json.loads(body)
    
    result = False
    if tableType == "selectTodayRow":
        result = handle_send_due_today_email(data.get('email'), data.get('title'), data.get('bookID'))
        return JSONResponse(content={"success": result}, status_code=200)
    elif tableType == "selectUpcomingRow":
        result = handle_send_due_soon_email(data.get('email'), data.get('title'), data.get('bookID'), data.get('dueDate'))
        return JSONResponse(content={"success": result}, status_code=200)
    elif tableType == "selectAvailRow":
        result = handle_send_avail_now_email(data.get('email'), data.get('title'), data.get('rating'), data.get('isbn'))
        return JSONResponse(content={"success": result}, status_code=200)
    
    return JSONResponse(content={"success": result}, status_code=400)