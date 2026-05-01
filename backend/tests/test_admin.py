from httpx import AsyncClient

from tests.helpers import _ADMIN_ROW, _USER_ROW, _admin_token, _user_token


async def test_list_users(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = [_USER_ROW, _ADMIN_ROW]

    resp = await client.get("/api/v1/admin/users", headers=_admin_token())

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_users_forbidden_for_user(client: AsyncClient):
    resp = await client.get("/api/v1/admin/users", headers=_user_token())

    assert resp.status_code == 403


async def test_list_users_with_pagination(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = [_USER_ROW]

    resp = await client.get(
        "/api/v1/admin/users?limit=10&offset=0", headers=_admin_token()
    )

    assert resp.status_code == 200


async def test_get_user_by_id(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _USER_ROW]

    resp = await client.get("/api/v1/admin/users/99", headers=_admin_token())

    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"


async def test_get_user_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, None]

    resp = await client.get("/api/v1/admin/users/999", headers=_admin_token())

    assert resp.status_code == 404


async def test_set_user_role(client: AsyncClient, mock_db_conn):
    promoted = {**_USER_ROW, "role": "admin"}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, promoted]

    resp = await client.patch(
        "/api/v1/admin/users/99/role",
        json={"role": "admin"},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


async def test_set_user_active_false(client: AsyncClient, mock_db_conn):
    deactivated = {**_USER_ROW, "is_active": False}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, deactivated]

    resp = await client.patch(
        "/api/v1/admin/users/99/active",
        json={"is_active": False},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
