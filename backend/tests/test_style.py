from httpx import AsyncClient

from tests.helpers import _ADMIN_ROW, _admin_token

_STYLE_JOIN_ROW = {
    "style_id": 1,
    "name": "Сальса",
    "description": "Латиноамериканский танец",
    "is_active": True,
    "image_id": None,
    "url": None,
    "sort_order": None,
}

_STYLE_CREATE_ROW = {
    "id": 1,
    "name": "Сальса",
    "description": "Латиноамериканский танец",
    "is_active": True,
}

_IMAGE_ROW = {
    "image_id": 10,
    "url": "https://example.com/salsa.jpg",
    "sort_order": 1,
}


async def test_get_all_styles(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_STYLE_JOIN_ROW]

    resp = await client.get("/api/v1/styles")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Сальса"


async def test_get_all_styles_empty(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/styles")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_style_by_id(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_STYLE_JOIN_ROW]

    resp = await client.get("/api/v1/styles/1")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Сальса"


async def test_get_style_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/styles/999")

    assert resp.status_code == 404


async def test_create_style(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _STYLE_CREATE_ROW]

    resp = await client.post(
        "/api/v1/styles",
        json={"name": "Сальса", "description": "Латиноамериканский танец"},
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Сальса"


async def test_create_style_forbidden(client: AsyncClient):
    resp = await client.post(
        "/api/v1/styles",
        json={"name": "Сальса", "description": "Латиноамериканский танец"},
    )

    assert resp.status_code == 401


async def test_update_style(client: AsyncClient, mock_db_conn):
    updated_join = {**_STYLE_JOIN_ROW, "name": "Бачата"}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.side_effect = [[_STYLE_JOIN_ROW], [updated_join]]

    resp = await client.patch(
        "/api/v1/styles/1",
        json={"name": "Бачата"},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Бачата"


async def test_update_style_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.patch(
        "/api/v1/styles/999",
        json={"name": "Что-то"},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_style(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.return_value = [_STYLE_JOIN_ROW]

    resp = await client.delete("/api/v1/styles/1", headers=_admin_token())

    assert resp.status_code == 204


async def test_delete_style_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.delete("/api/v1/styles/999", headers=_admin_token())

    assert resp.status_code == 404


async def test_add_image(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _IMAGE_ROW]
    mock_db_conn.fetch.return_value = [_STYLE_JOIN_ROW]

    resp = await client.post(
        "/api/v1/styles/1/images",
        json={"url": "https://example.com/salsa.jpg", "sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["url"] == "https://example.com/salsa.jpg"


async def test_update_image(client: AsyncClient, mock_db_conn):
    updated_image = {**_IMAGE_ROW, "sort_order": 3}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, updated_image]

    resp = await client.patch(
        "/api/v1/styles/images/10",
        json={"sort_order": 3},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["sort_order"] == 3


async def test_update_image_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, None]

    resp = await client.patch(
        "/api/v1/styles/images/999",
        json={"sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_image(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 10}]

    resp = await client.delete(
        "/api/v1/styles/images/10", headers=_admin_token()
    )

    assert resp.status_code == 204
