from fastapi import APIRouter, Body, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from controllers.token import *
from controllers.user_controller import *
from fastapi.responses import JSONResponse

MANAGER_LOGIN_PAGE = "https://34.47.39.132/auth/manager"
MANAGER_DASHBOARD_PAGE = "https://34.47.39.132/catalog/dashboard"
MANAGER_CATALOG_PAGE = "https://34.47.39.132/catalog/view-inventory"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/main", response_class=HTMLResponse)
def main_page(request: Request):
    manager_name = request.cookies.get("manager_name", "Admin")
    return templates.TemplateResponse("manage_users_main.html", {"request": request, "manager": manager_name})

@router.get("/manager-login", response_class=HTMLResponse)
def manager_login_page(response: Response):
    response = RedirectResponse(url=MANAGER_LOGIN_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("manager_login_token")
    response.delete_cookie("manager_name")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(response: Response):
    response = RedirectResponse(url=MANAGER_DASHBOARD_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.get("/catalog", response_class=HTMLResponse)
def catalog_page(response: Response):
    response = RedirectResponse(url=MANAGER_CATALOG_PAGE, status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.get("/all-users")
def get_all_users(request: Request):
    return handle_get_users()

@router.get("/add-user/")
def add_user_page(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})

@router.get("/edit-user/{email}/{status}")
def modify_user_page(email: str, status: str, request: Request):
    return templates.TemplateResponse("edit_user.html", {"request": request, "email": email, "status": status})

@router.get("/delete-user/{email}/{status}")
def delete_user_page(email: str, status: str, request: Request):
    return templates.TemplateResponse("delete_user.html", {"request": request, "email": email, "status": status})

@router.get("/customer-info/{user_email}")
def get_user_data(user_email: str):
    email = user_email.split(' ')
    if len(email) == 2:
        metadata = get_manager_metadata(email[1])
    else:
        metadata = get_customer_metadata(email[0])
    return metadata
    
@router.post("/users/delete-user/{username}")
def delete_user(username: str, request: Request):
    # the manager cannot delete their own account
    token = request.cookies.get("manager_login_token")
    if not token:
        return JSONResponse(status_code=409, content={"message": "Your session has expired. Please login again."})
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    managerID = payload.get('sub')
    
    if username == managerID:
        result = JSONResponse(status_code=409, content={"message": "Error cannot delete your own admin account!"})
        return result
    
    if '@' in username:
        result = delete_customer(username)
    else:
        result = delete_manager(username)
    return result
    
@router.post("/users/edit-user/{username}")
def edit_user(request: Request, username: str, firstName: str = Form(...), lastName: str = Form(...), age: int = Form(None), email: str = Form(...), managerID: str = Form(None)):
    # the manager cannot edit their own account
    token = request.cookies.get("manager_login_token")
    if not token:
        return JSONResponse(status_code=409, content={"message": "Your session has expired. Please login again."})
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    manager_id = payload.get('sub')
    
    if username == manager_id:
        result = JSONResponse(status_code=409, content={"message": "Error cannot edit your own admin account!"})
        return result
    
    if '@' in username:
        result = edit_customer(username, firstName, lastName, age, email)
    else:
        result = edit_manager(username, firstName, lastName, email, managerID)

    return result

@router.post("/users/add-user")
def add_user(request: Request, firstName: str = Form(...), lastName: str = Form(...), age: int = Form(None), email: str = Form(...), managerID: str = Form(None), isManager: bool = Form(...), password: str = Form(...)):
    print(firstName,lastName,age,email,password,managerID,isManager)
    token = request.cookies.get("manager_login_token")
    if not token:
        return JSONResponse(status_code=409, content={"message": "Your session has expired. Please login again."})
    
    if isManager:
        result = add_manager(firstName, lastName, email, password, managerID)
    else:  # If the user is a regular customer
        result = add_customer(firstName, lastName, age, email, password)
    
    return result