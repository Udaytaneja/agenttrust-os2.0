import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, select

from backend.app.core.database import AsyncSessionLocal
from backend.app.main import app
from backend.app.models.user import User
from backend.app.core.security import hash_password, verify_password


@pytest.mark.asyncio
async def test_auth_regression_suite():
    """
    Comprehensive regression test covering:
    1. Valid credentials produce successful login response with access_token and refresh_token
    2. Invalid credentials produce HTTP 401 Unauthorized
    3. Inactive accounts are rejected
    4. Password hashing and verification compatibility (Argon2 / pwdlib)
    5. Token structure and response format matches frontend expectations
    """
    test_email = "test-regression-applicant@apextech.com"
    test_pass = "ApplicantSecurePass123!"

    # 1. Hashing compatibility check
    hashed = hash_password(test_pass)
    assert verify_password(test_pass, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    # Ensure unicode bullet characters are rejected
    assert verify_password("••••••••••••", hashed) is False

    # 2. Database seed & teardown
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Valid login
        valid_res = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": test_pass},
        )
        assert valid_res.status_code == 200
        data = valid_res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_email
        assert data["user"]["role"] == "user"

        # Test 2: Invalid password returns 401
        invalid_res = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": "WrongPassword!"},
        )
        assert invalid_res.status_code == 401
        assert "Invalid email or password" in invalid_res.json().get("detail", "")

        # Test 3: Literal bullet characters return 401 (reproducing original bug)
        bullet_res = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": "••••••••••••"},
        )
        assert bullet_res.status_code == 401

        # Test 4: Inactive account cannot log in
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(User).where(User.email == test_email))
            db_user = res.scalar_one()
            db_user.is_active = False
            await session.commit()

        inactive_res = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": test_pass},
        )
        assert inactive_res.status_code == 401

    # Final cleanup
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM users WHERE email = :email"), {"email": test_email})
        await session.commit()
