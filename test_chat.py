import requests

BASE_URL = "http://localhost:8000/api"

print("Logging in...")
res = requests.post(f"{BASE_URL}/users/login", data={"username": "test_user_prod@example.com", "password": "password123"})
token = res.json()["access_token"]

print("Chatting...")
user_headers = {"Authorization": f"Bearer {token}"}
try:
    res = requests.post(f"{BASE_URL}/chat", headers=user_headers, json={"user_email": "test_user_prod@example.com", "question": "Hello!"}, timeout=30)
    print("Chat status:", res.status_code)
    try:
        print(res.json())
    except:
        print(res.text)
except Exception as e:
    print("FAILED:", type(e), e)
