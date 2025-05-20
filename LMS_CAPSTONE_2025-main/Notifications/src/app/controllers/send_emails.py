import requests

# MORE INFO: https://app.brevo.com/settings/keys/smtp

def send_due_today_email(email, title, name, today_date, bookID):
    
    API_KEY = "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"
    SENDER_EMAIL = "lmscapstone38@gmail.com"
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "templateID": 4,
        "params": {"title": title, "name": name, "today": today_date, "bookID": bookID},
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("\n\nEmail sent successfully!\n\n")
        return True
    else:
        print(f"\n\nFailed to send email: {response.status_code} - {response.text}\n\n")
        return False

def send_due_soon_email(email, title, name, bookID, dueDate):
    
    API_KEY = "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"
    SENDER_EMAIL = "lmscapstone38@gmail.com"
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "templateID": 5,
        "params": {"title": title, "name": name, "bookID": bookID, "dueDate": dueDate},
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("\n\nEmail sent successfully!\n\n")
        return True
    else:
        print(f"\n\nFailed to send email: {response.status_code} - {response.text}\n\n")
        return False

def send_avail_now_email(email, title, name, rating, isbn):
    
    API_KEY = "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"
    SENDER_EMAIL = "lmscapstone38@gmail.com"
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "LMS CAPSTONE", "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "templateID": 10,
        "params": {"title": title, "name": name, "rating": rating, "isbn": isbn},
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("\n\nEmail sent successfully!\n\n")
        return True
    else:
        print(f"\n\nFailed to send email: {response.status_code} - {response.text}\n\n")
        return False