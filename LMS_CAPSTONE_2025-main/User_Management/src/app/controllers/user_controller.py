from controllers.token import *
from models.books import *
from models.customers import *
from models.managers import *

def handle_get_users():
    users_list = []

    # Get dictionary of customers
    customers = list_users()
    for c in customers:
        users_list.append({
            "name": f"{c['firstName']} {c['lastName']}",
            "email": c['email'],
            "status": "Customer",
            "created_on": customer_created_on_date(c)
        })

    # Get dictionary of managers
    managers = list_managers()
    for m in managers:
        users_list.append({
            "name": f"{m['firstName']} {m['lastName']}",
            "email": f"{m['email']} ({m['managerID']})",
            "status": "Manager",
            "created_on": manager_created_on_date(m)
        })

    users_list.sort(key=lambda x: x["created_on"])
    return users_list

        
    