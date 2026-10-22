import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import urllib.request
import json
from sqlalchemy import text, select

os.environ["APP_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///D:/Agenttrust-os-/local_dev.db"
os.environ["JWT_SECRET"] = "local-test-dev-secret-key-1234567890-test"

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.core.security import hash_password, verify_password

def make_req(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8")) if e.fp else {}
        return e.code, body

async def run_regression():
    test_email = "test-regression-applicant@apextech.com"
    test_pass = "ApplicantSecurePass123!"

    print("--- 1. Testing Hashing & Verification Logic ---")
    hashed = hash_password(test_pass)
    assert verify_password(test_pass, hashed) is True, "Valid password verification failed"
    assert verify_password("WrongPassword123!", hashed) is False, "Wrong password unexpectedly succeeded"
    assert verify_password("••••••••••••", hashed) is False, "Bullet password unexpectedly succeeded"
    print("PASS: Hashing and password verification working as expected.")

    print("--- 2. Setting Up Test User in Isolated Local DB ---")
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM users WHERE email = :email"), {"email": test_email})
        user = User(
            name="Regression Applicant",
            email=test_email,
            hashed_password=hashed,
            phone="1234567890",
            role="user",
            language="en",
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
    print("PASS: Test user seeded successfully.")

    print("--- 3. Testing Valid Login API Request ---")
    status, data = make_req("http://127.0.0.1:8000/api/v1/auth/login", {"email": test_email, "password": test_pass})
    assert status == 200, f"Expected 200, got {status}"
    assert "access_token" in data, "access_token missing in response"
    assert "refresh_token" in data, "refresh_token missing in response"
    assert data["token_type"] == "bearer", f"Unexpected token_type: {data.get('token_type')}"
    assert data["user"]["email"] == test_email, "User email mismatch"
    assert data["user"]["role"] == "user", "User role mismatch"
    print("PASS: Valid login returns HTTP 200 with tokens and user info.")

    print("--- 4. Testing Invalid Password Rejection ---")
    status, data = make_req("http://127.0.0.1:8000/api/v1/auth/login", {"email": test_email, "password": "WrongPassword123!"})
    assert status == 401, f"Expected 401, got {status}"
    msg = data.get("error", {}).get("message") or data.get("detail")
    assert msg == "Invalid email or password", f"Unexpected error message: {data}"
    print("PASS: Invalid password correctly rejected with HTTP 401 and standard error payload.")

    print("--- 5. Testing Bullet Characters Form Rejection ---")
    status, data = make_req("http://127.0.0.1:8000/api/v1/auth/login", {"email": test_email, "password": "••••••••••••"})
    assert status == 401, f"Expected 401, got {status}"
    print("PASS: Bullet characters correctly rejected with HTTP 401.")

    print("--- 6. Testing Inactive Account Rejection ---")
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.email == test_email))
        db_user = res.scalar_one()
        db_user.is_active = False
        await session.commit()

    status, data = make_req("http://127.0.0.1:8000/api/v1/auth/login", {"email": test_email, "password": test_pass})
    assert status == 401, f"Expected 401, got {status}"
    print("PASS: Inactive account correctly rejected.")

    # Cleanup
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM users WHERE email = :email"), {"email": test_email})
        await session.commit()
    print("PASS: Teardown completed.")
    print("\nALL REGRESSION TESTS PASSED.")

if __name__ == "__main__":
    asyncio.run(run_regression())
