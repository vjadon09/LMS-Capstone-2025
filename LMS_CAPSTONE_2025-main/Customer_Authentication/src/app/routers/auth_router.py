from fastapi import APIRouter, Form, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from controllers.authentication import *
from controllers.token import *
from controllers.email_verif_code import *
from datetime import datetime, timedelta
import os
from urllib.parse import urlencode
from slowapi import Limiter

CATALOG_SERVICE_URL = "https://34.47.39.132/catalog"
USER_HOME_PAGE = "https://34.47.39.132/search/home"
MYLIBRARY_PAGE = "https://34.47.39.132/mylib"

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")

templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

def get_client_ip(request: Request):
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

limiter = Limiter(key_func=get_client_ip)
app = FastAPI()
app.state.limiter = limiter

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    login_token = request.cookies.get("login_token")
    if login_token:
        try:
            verify_jwt(login_token)
            return RedirectResponse(url="/auth/home", status_code=status.HTTP_303_SEE_OTHER)
        except HTTPException:
            pass
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(email: str = Form(), pword: str = Form()):
    jwt_token = handle_login(email, pword) 
    if jwt_token:
        expiration_time = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION_TIME)
        expires = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response = RedirectResponse(url="/auth/home", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="login_token", value=jwt_token, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)
        
        user = get_user(email)
        user_name = user.firstName if user else "Guest"
        response.set_cookie(key="user_name", value=user_name, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)
        return response
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"}
        )

@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

# Route to handle logout
@router.post("/logout", response_class=HTMLResponse)
async def logout(response: Response):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("login_token")
    response.delete_cookie("user_name")
    return response

# Route to show registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route to handle user registration
@router.post("/register")
async def register_user(fname: str = Form(...), lname: str = Form(...), email: str = Form(...), password: str = Form(...), age: int = Form(...)):
    result = handle_registration(fname, lname, email, password, age)
    if result == "Error":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Email is already registered."}
        )
    send_register_email(email, fname, lname)
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

# Route to show forgot password page
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# Route to handle password reset
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(response: Response, request: Request, email: str = Form(...)):
    result = handle_forgot_password(email)
    if result:
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        expires = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        verif_code = generate_code()
        code_token = generate_code_token(verif_code, expiration_time) 
        
        response = RedirectResponse(url="/auth/verification-code", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="verif_code", value=code_token, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)
        response.set_cookie(key="verif_email", value=email, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)
            
        send_verif_email(email, verif_code)
        return response
    
    return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Email is not registered."})   

@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return RedirectResponse(url=USER_HOME_PAGE ,status_code=status.HTTP_303_SEE_OTHER)

@router.get("/verification-code", response_class=HTMLResponse)
async def verification_code_page(request: Request):
    return templates.TemplateResponse("verification_code.html", {"request": request})

@router.post("/verification-code", response_class=HTMLResponse)
async def verification_code(request: Request, code: int = Form(...)):
    isValid = validate_code(request, code)
    if isValid:
        response = RedirectResponse(url="/auth/reset-password", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("verif_code")
        return response
    return templates.TemplateResponse("verification_code.html", {"request": request, "error": "Invalid verification code."})

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/reset_password", response_class=HTMLResponse)
async def reset_password(request: Request, first: str = Form(...), second: str = Form(...)):
    result = handle_reset_password(request, first, second)
    if result == "Password updated successfully":
        response = JSONResponse(
            status_code=200,
            content={"success": "Password changed successfully"})
        response.delete_cookie("verif_email")
        return response
    elif result == "New password must be different from old password":
        response = JSONResponse(
            status_code=409,
            content={"error": "New password must be different from old password"})
        return response
    
    return JSONResponse(
            status_code=400,
            content={"error": "Passwords do not match"})

@router.get("/cancel-verif", response_class=HTMLResponse)
async def cancel_verif(request: Request):
    response = RedirectResponse(url="/auth/login" ,status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("verif_email")
    response.delete_cookie("verif_code")
    return response

# Manager login routes

@router.get("/manager", response_class=HTMLResponse)
async def manager_login_page(request: Request):
    return templates.TemplateResponse("manager_login.html", {"request": request})

@router.post("/manager")
def manager_login(manager_id: str = Form(), password: str = Form()):
    jwt_token = handle_manager_login(manager_id, password)
    
    if jwt_token:
        expiration_time = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION_TIME)
        expires = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # to be changed
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"url": CATALOG_SERVICE_URL})
        #response = RedirectResponse(url=CATALOG_SERVICE_URL, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="manager_login_token", value=jwt_token, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)

        manager = get_manager(manager_id)
        manager_name = manager.firstName if manager else "Manager"
        response.set_cookie(key="manager_name", value=manager_name, httponly=True, samesite="None", secure=True , path="/", expires=expires, max_age=TOKEN_EXPIRATION_TIME)

        return response
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid manager ID or password"}
        )

@router.get("/admin_dashboard", response_class = HTMLResponse)
async def get_admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.get("/mylibrary", response_class = HTMLResponse)
async def get_mylib_page():
    return RedirectResponse(MYLIBRARY_PAGE, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/aboutus", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# sending emails to the developers of the website

API_KEY = "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"
SENDER_EMAIL = "lmscapstone38@gmail.com"

@router.post("/send-message")
@limiter.limit("60/minute")
async def send_message(request: Request):
    data = await request.json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return JSONResponse(status_code=400, content={"error": "Missing required fields"})

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": "m14patel@torontomu.ca"}, {"email": "vjadon@torontomu.ca"}, {"email": "astha.patel@torontomu.ca"}, {"email": "atiya.azeez@torontomu.ca"}],
        "replyTo": {"email": email, "name": name},
        "subject": f"New message from {name}",
        "htmlContent": f"""
            <p><strong>From:</strong> {name} ({email})</p>
            <p><strong>Message:</strong><br>{message}</p>
        """
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return JSONResponse(status_code=200, content={"message": "Message sent successfully!"})
    else:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to send email: {response.status_code} - {response.text}"}
        )