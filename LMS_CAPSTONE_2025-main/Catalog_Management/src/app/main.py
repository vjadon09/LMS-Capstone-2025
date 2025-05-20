from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.catalogRouter import router as catalog_router
import uvicorn, os, ssl
from fastapi import Request, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from models.database.db import get_db, close_db
from fastapi.responses import RedirectResponse
from controllers.token import *

load_dotenv(dotenv_path='./app/config/.env')

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware example
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Custom middleware: Before request processing")
        response = await call_next(request)
        print("Custom middleware: After request processing")
        return response

# app.add_middleware(CustomMiddleware)

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "views", "static")
templates_dir = os.path.join(base_dir, "views", "templates")

app.mount("/catalog/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
def startup_db_client():
    try:
        # Test MongoDB connection
        get_db().client.admin.command('ping')
        print("MongoDB connected successfully!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Unable to connect to MongoDB")

@app.on_event("shutdown")
def shutdown_db_client():
    close_db()
    print("MongoDB connection closed!")

app.include_router(catalog_router, prefix="/catalog")

@app.get("/catalog")
async def root(request: Request):
    login_token = request.cookies.get("manager_login_token")
    if login_token:
        try:
            verify_jwt(login_token)
            return RedirectResponse(url="/catalog/admin_dashboard", status_code=status.HTTP_303_SEE_OTHER)
        except HTTPException:
            pass
    return RedirectResponse(url="/catalog/manager-login", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8002,  # Use a different port
        reload=True if os.environ.get("ENVIRONMENT") == "dev" else False,
        workers=1,
        proxy_headers=True
    )