import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def print_result(name, res):
    print(f"=== {name} ===")
    print(f"Status: {res.status_code}")
    try:
        print(res.json())
    except:
        print(res.text)
    print("-" * 40)

# 1. User Signup
user_data = {"name": "Test User", "email": "test_user_prod@example.com", "password": "password123"}
res = requests.post(f"{BASE_URL}/users/signup", json=user_data)
# Ignore 400 if already exists
if res.status_code not in [200, 400]:
    print_result("User Signup Failed", res)

# 2. User Login
res = requests.post(f"{BASE_URL}/users/login", data={"username": user_data["email"], "password": user_data["password"]})
print_result("User Login", res)
user_token = res.json().get("access_token")
user_headers = {"Authorization": f"Bearer {user_token}"}

# 3. User Get Me
res = requests.get(f"{BASE_URL}/users/me", headers=user_headers)
print_result("User Get Me", res)

# 4. User Chat (Greeting)
res = requests.post(f"{BASE_URL}/chat", headers=user_headers, json={"user_email": user_data["email"], "question": "Hello!"})
print_result("User Chat (Greeting)", res)

# 5. User Chat (Ticket Trigger)
res = requests.post(f"{BASE_URL}/chat", headers=user_headers, json={"user_email": user_data["email"], "question": "How do I build a fusion reactor?"})
print_result("User Chat (Ticket Trigger)", res)

# 6. User Chat History
res = requests.get(f"{BASE_URL}/chat/history/{user_data['email']}", headers=user_headers)
print_result("User Chat History", res)

# 7. Admin Secret Login
res = requests.post(f"{BASE_URL}/users/admin-secret-login", json={"secret_code": "resolvai2026"})
print_result("Admin Secret Login", res)
admin_token = res.json().get("access_token")
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 8. Admin Get Users
res = requests.get(f"{BASE_URL}/users", headers=admin_headers)
print_result("Admin Get All Users", res)

# 9. Admin Get Tickets
res = requests.get(f"{BASE_URL}/tickets", headers=admin_headers)
print_result("Admin Get All Tickets", res)
tickets = res.json()
ticket_id = tickets[0]["id"] if tickets else None

# 10. Admin Update Ticket (if ticket exists)
if ticket_id:
    res = requests.put(f"{BASE_URL}/tickets/{ticket_id}", headers=admin_headers, json={"status": "resolved"})
    print_result("Admin Update Ticket", res)

# 11. Admin Upload Docs
with open("test_doc.txt", "w") as f:
    f.write("This is a test document for the production readiness check.")
with open("test_doc.txt", "rb") as f:
    res = requests.post(f"{BASE_URL}/admin/upload-docs", headers=admin_headers, files={"files": ("test_doc.txt", f)}, data={"wipe_existing": "false"})
print_result("Admin Upload Docs", res)
os.remove("test_doc.txt")

# 12. Admin Retrain
res = requests.post(f"{BASE_URL}/admin/retrain", headers=admin_headers)
print_result("Admin Retrain AI", res)

