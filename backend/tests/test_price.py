from httpx import AsyncClient

from tests.helpers import _ADMIN_ROW, _admin_token

_PLAN_JOIN_ROW = {
    "plan_id": 1,
    "name": "Базовый",
    "description": "4 занятия в месяц",
    "price": 3000,
    "subtitle": "Для начинающих",
    "is_active": True,
    "is_recommended": False,
    "sort_order": 1,
    "option_id": None,
    "text": None,
    "option_sort_order": None,
}

_PLAN_CREATE_ROW = {
    "id": 1,
    "name": "Базовый",
    "description": "4 занятия в месяц",
    "price": 3000,
    "subtitle": "Для начинающих",
    "is_active": True,
    "is_recommended": False,
    "sort_order": 1,
}

_OPTION_ROW = {
    "option_id": 10,
    "text": "Доступ к онлайн-материалам",
    "sort_order": 1,
}


async def test_get_all_plans(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_PLAN_JOIN_ROW]

    resp = await client.get("/api/v1/prices")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Базовый"


async def test_get_all_plans_empty(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/prices")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_plan_by_id(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_PLAN_JOIN_ROW]

    resp = await client.get("/api/v1/prices/1")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Базовый"


async def test_get_plan_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/prices/999")

    assert resp.status_code == 404


async def test_create_plan(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _PLAN_CREATE_ROW]

    resp = await client.post(
        "/api/v1/prices",
        json={
            "name": "Базовый",
            "description": "4 занятия в месяц",
            "price": 3000,
            "subtitle": "Для начинающих",
            "sort_order": 1,
        },
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Базовый"


async def test_create_plan_forbidden(client: AsyncClient):
    resp = await client.post(
        "/api/v1/prices",
        json={
            "name": "Базовый",
            "description": "4 занятия в месяц",
            "price": 3000,
            "subtitle": "Для начинающих",
            "sort_order": 1,
        },
    )

    assert resp.status_code == 401


async def test_update_plan(client: AsyncClient, mock_db_conn):
    updated_join = {**_PLAN_JOIN_ROW, "name": "Продвинутый"}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.side_effect = [[_PLAN_JOIN_ROW], [updated_join]]

    resp = await client.patch(
        "/api/v1/prices/1",
        json={"name": "Продвинутый"},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Продвинутый"


async def test_update_plan_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.patch(
        "/api/v1/prices/999",
        json={"name": "Что-то"},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_plan(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.return_value = [_PLAN_JOIN_ROW]

    resp = await client.delete("/api/v1/prices/1", headers=_admin_token())

    assert resp.status_code == 204


async def test_delete_plan_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.delete("/api/v1/prices/999", headers=_admin_token())

    assert resp.status_code == 404


async def test_add_option(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _OPTION_ROW]
    mock_db_conn.fetch.return_value = [_PLAN_JOIN_ROW]

    resp = await client.post(
        "/api/v1/prices/1/options",
        json={"text": "Доступ к онлайн-материалам", "sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["text"] == "Доступ к онлайн-материалам"


async def test_update_option(client: AsyncClient, mock_db_conn):
    updated_option = {**_OPTION_ROW, "sort_order": 5}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, updated_option]

    resp = await client.patch(
        "/api/v1/prices/options/10",
        json={"sort_order": 5},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["sort_order"] == 5


async def test_update_option_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, None]

    resp = await client.patch(
        "/api/v1/prices/options/999",
        json={"sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_option(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 10}]

    resp = await client.delete(
        "/api/v1/prices/options/10", headers=_admin_token()
    )

    assert resp.status_code == 204
