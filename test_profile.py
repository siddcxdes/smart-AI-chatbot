import requests

BASE_URL = "http://localhost:8000/api"

print("Logging in...")
res = requests.post(f"{BASE_URL}/users/login", data={"username": "test_user_prod@example.com", "password": "password123"})
print(res.status_code, res.json())
token = res.json()["access_token"]

print("Getting me...")
try:
    res = requests.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(res.status_code, res.json())
except Exception as e:
    print("FAILED:", type(e), e)
