from controllers.token import *
from controllers.email_verif_code import *
from models.customers import *
from models.managers import *

def verify_user(email: str, password: str):
    user = get_user(email)
    if not user or user.password != password:
        return False
    return True

# Logic for handling login
def handle_login(email: str, pword: str):
    if verify_user(email, pword):
        token = create_jwt(email)
        return token
    else:
        return None

# Logic for handling registration
def handle_registration(fname: str, lname: str, email: str, password: str, age: int):
    user = get_user(email)
    manager = get_manager_by_email(email)
    if user is None and manager is None:
        return create_user(Customer(firstName=fname, lastName=lname, email=email, password=password, 
                                    address=Address(streetAddress="", city="", state="", country=""), 
                                    age=age, wishlist=Wishlist(items=[])))
    return "Error"  
    
# Logic for handling forgot password
def handle_forgot_password(email: str):
    user = get_user(email)
    manager = get_manager_by_email(email)
    if user is None and manager is not None:
        return True
    elif user is not None and manager is None:
        return True
    return False

def handle_reset_password(request: Request, first_pass: str, second_pass: str):
    verif_email = get_verif_email(request)
    if first_pass == second_pass:
        response = change_password(verif_email, first_pass)
        if response and response["message"]:
            return response["message"]
    return None

def verify_manager(manager_id: str, password: str):
    manager = get_manager(manager_id)
    if manager is None:
        return False
    elif manager_id != manager.managerID or password != manager.passwordHash:
        return False
    return True

def handle_manager_login(manager_id: str, password: str):
    if verify_manager(manager_id, password):
        token = create_jwt(manager_id)
        return token
    else:
        return None
    
    