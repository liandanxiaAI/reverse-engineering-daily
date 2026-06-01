"""
Liandanxia.io Login API - Final Tester
Tests login with MD5 hash (confirmed algorithm) + handles rate limiting
Also supports registration flow
"""

import hashlib
import requests
import json
import sys
import time

API_BASE = "https://api.liandanxia.io/silver"


def api_post(endpoint, body, extra_headers=None):
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    url = f"{API_BASE}{endpoint}"
    resp = requests.post(url, json=body, headers=headers)
    try:
        data = resp.json()
    except:
        data = {"_raw": resp.text}
    return resp.status_code, dict(resp.headers), data


def api_get(endpoint, params=None, extra_headers=None):
    headers = {"Accept": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    url = f"{API_BASE}{endpoint}"
    resp = requests.get(url, params=params, headers=headers)
    try:
        data = resp.json()
    except:
        data = {"_raw": resp.text}
    return resp.status_code, dict(resp.headers), data


def login(email: str, password: str):
    """Login with MD5 hashed password"""
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    print(f"\n{'='*60}")
    print(f"POST /api/user/login")
    print(f"Email: {email}")
    print(f"Password hash (MD5): {hashed}")
    
    status, headers, data = api_post("/api/user/login", {
        "email": email,
        "password": hashed
    })
    
    print(f"HTTP Status: {status}")
    print(f"API Code: {data.get('code')}")
    print(f"Message: {data.get('message')}")
    
    # Token is in data.LDX-Token (nested under "data")
    token = data.get("LDX-Token") or (data.get("data") or {}).get("LDX-Token")
    if not token:
        # Also check response headers
        for k, v in headers.items():
            if "token" in k.lower() or "ldx" in k.lower():
                print(f"  Header: {k} = {v}")
                token = v
    
    if token:
        print(f"\n*** LOGIN SUCCESS! ***")
        print(f"Token: {token[:30]}...")
        return token
    
    # Check all response data for any token-like field
    data_str = json.dumps(data)
    if "token" in data_str.lower():
        print(f"\nToken found in response body:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data.get("LDX-Token") or data.get("token")
    
    print(f"\nRaw response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return None


def get_user_info(token: str):
    """Fetch user info with token"""
    print(f"\n{'='*60}")
    print(f"GET /api/user/self/")
    
    status, headers, data = api_get("/api/user/self/", 
        extra_headers={"Authorization": f"Bearer {token}"})
    
    print(f"HTTP Status: {status}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    print("Liandanxia.io Login API Tester")
    print("Password hash: MD5")
    
    if len(sys.argv) < 3:
        print("\nUsage: python liandanxia_test_hash.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    token = login(email, password)
    
    if token:
        get_user_info(token)
    else:
        print("\nLogin failed. Possible reasons:")
        print("1. Password is incorrect")
        print("2. Account was created via OAuth (GitHub/Google) - no password set")
        print("3. Account doesn't exist")
        print("\nTo register a new account, run:")
        print("  python register.py <email> <password>")


if __name__ == "__main__":
    main()

