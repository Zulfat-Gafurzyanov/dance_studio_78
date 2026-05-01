from httpx import AsyncClient

from tests.helpers import _USER_ROW, _user_token


async def test_get_profile(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_USER_ROW, _USER_ROW]

    resp = await client.get("/api/v1/users/me", headers=_user_token(user_id=99))

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "user@example.com"
    assert body["role"] == "user"


async def test_get_profile_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")

    assert resp.status_code == 401


async def test_get_profile_blocked(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = {**_USER_ROW, "is_active": False}

    resp = await client.get("/api/v1/users/me", headers=_user_token(user_id=99))

    assert resp.status_code == 401


async def test_update_profile_email(client: AsyncClient, mock_db_conn):
    updated = {**_USER_ROW, "email": "new@example.com"}
    mock_db_conn.fetchrow.side_effect = [_USER_ROW, updated]

    resp = await client.patch(
        "/api/v1/users/me",
        json={"email": "new@example.com"},
        headers=_user_token(user_id=99),
    )

    assert resp.status_code == 200
    assert resp.json()["email"] == "new@example.com"


async def test_update_profile_password(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_USER_ROW, _USER_ROW]

    resp = await client.patch(
        "/api/v1/users/me",
        json={"password": "NewPass123"},
        headers=_user_token(user_id=99),
    )

    assert resp.status_code == 200


async def test_delete_account(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _USER_ROW
    mock_db_conn.execute.return_value = "DELETE 1"

    resp = await client.delete("/api/v1/users/me", headers=_user_token(user_id=99))

    assert resp.status_code == 204
