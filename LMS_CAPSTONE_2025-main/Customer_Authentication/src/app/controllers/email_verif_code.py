from fastapi import Request
import secrets, jwt, requests, random
from datetime import datetime, timezone

def generate_code():
    return random.randint(100000, 999999)

def generate_code_token(code, expiration_time):
    SECRET_KEY = "lmscapstone"
    payload = {
        "iss": "FastAPI",
        "sub": str(code),
        "exp": expiration_time
    }
    verif_code_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return verif_code_token

def get_verif_code(request: Request):
    verif_code = request.cookies.get("verif_code")
    return verif_code

def get_verif_email(request: Request):
    verif_email = request.cookies.get("verif_email")
    return verif_email

def validate_code(request: Request, entered_code: str):
    verif_code = get_verif_code(request)
    SECRET_KEY = "lmscapstone"
    decoded_payload = jwt.decode(verif_code, SECRET_KEY, algorithms="HS256")
    
    if str(entered_code) != decoded_payload["sub"]:
        return False
    if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded_payload["exp"], tz=timezone.utc):
       return False

    return True

def send_verif_email(email, code):
    # MORE INFO: https://app.brevo.com/settings/keys/smtp
    API_KEY = "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"
    SENDER_EMAIL = "lmscapstone38@gmail.com"

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "templateID": 1,
        "params": {"verif_code": code},
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("\n\nEmail sent successfully!\n\n")
    else:
        print(f"\n\nFailed to send email: {response.status_code} - {response.text}\n\n")
        
def send_register_email(email, fName, lName):
    # MORE INFO: https://app.brevo.com/settings/keys/smtp
    API_KEY = "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"
    SENDER_EMAIL = "lmscapstone38@gmail.com"

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "templateID": 3,
        "params": {"firstName": fName, "lastName": lName, "email": email},
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("\n\nRegistration email sent successfully!\n\n")
    else:
        print(f"\n\nFailed to send email: {response.status_code} - {response.text}\n\n")