from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional
import jwt

router = APIRouter()

SECRET_KEY = "lmscapstone"
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 3600

# token creation code
def create_jwt(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION_TIME)
    payload = {
        "iss": "FastAPI",
        "sub": email,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# validate  token code
def verify_jwt(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        expiration = payload.get("exp")
        
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
        if datetime.utcfromtimestamp(expiration) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    
        return {"subject": email}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
        
def get_user_email_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    
        return email
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )