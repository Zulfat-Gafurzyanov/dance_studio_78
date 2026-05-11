from asyncpg import UniqueViolationError
from httpx import AsyncClient

import src.core.security as security


async def test_sign_up_success(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = {
        "id": 1,
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z",
    }

    resp = await client.post(
        "/api/v1/auth/sign-up",
        json={
            "email": "test@example.com",
            "password": "StrongPass1",
            "password_confirm": "StrongPass1",
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in resp.cookies

    payload = security.decode_access_token(body["access_token"])
    assert payload["user_id"] == 1
    assert payload["role"] == "user"


async def test_sign_up_passwords_mismatch(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/sign-up",
        json={
            "email": "test@example.com",
            "password": "StrongPass1",
            "password_confirm": "DifferentPass1",
        },
    )
    assert resp.status_code == 422


async def test_sign_in_returns_valid_jwt(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = {
        "id": 42,
        "email": "user@example.com",
        "password_hash": security.hash_password("StrongPass1"),
        "role": "user",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z",
    }

    resp = await client.post(
        "/api/v1/auth/sign-in",
        json={"email": "user@example.com", "password": "StrongPass1"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in resp.cookies

    payload = security.decode_access_token(body["access_token"])
    assert payload["user_id"] == 42
    assert payload["role"] == "user"


async def test_sign_in_invalid_email(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = None

    resp = await client.post(
        "/api/v1/auth/sign-in",
        json={
            "email": "nonexistent@example.com",
            "password": "StrongPass1",
        },
    )
    assert resp.status_code == 401


async def test_sign_in_wrong_password(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = {
        "id": 1,
        "email": "user@example.com",
        "password_hash": security.hash_password("CorrectPass1"),
        "role": "user",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z",
    }

    resp = await client.post(
        "/api/v1/auth/sign-in",
        json={"email": "user@example.com", "password": "WrongPass1"},
    )
    assert resp.status_code == 401


async def test_sign_in_blocked_account(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = {
        "id": 1,
        "email": "user@example.com",
        "password_hash": security.hash_password("StrongPass1"),
        "role": "user",
        "is_active": False,
        "created_at": "2025-01-01T00:00:00Z",
    }

    resp = await client.post(
        "/api/v1/auth/sign-in",
        json={"email": "user@example.com", "password": "StrongPass1"},
    )
    assert resp.status_code == 403


async def test_sign_up_email_already_taken(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = UniqueViolationError("duplicate key")

    resp = await client.post(
        "/api/v1/auth/sign-up",
        json={
            "email": "existing@example.com",
            "password": "StrongPass1",
            "password_confirm": "StrongPass1",
        },
    )
    assert resp.status_code == 409
