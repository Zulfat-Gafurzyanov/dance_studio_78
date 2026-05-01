from httpx import AsyncClient

from tests.helpers import _ADMIN_ROW, _admin_token

_INFO_ROW = {
    "id": 1,
    "year_opened": 2010,
    "students_count": 500,
    "phone": "+7 (999) 123-45-67",
    "address": "ул. Танцевальная, 1",
    "working_hours": "Пн-Пт 9:00–21:00",
    "email": "studio@example.com",
}


async def test_get_studio_info(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _INFO_ROW

    resp = await client.get("/api/v1/studio-info")

    assert resp.status_code == 200
    body = resp.json()
    assert body["year_opened"] == 2010
    assert body["phone"] == "+7 (999) 123-45-67"


async def test_get_studio_info_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = None

    resp = await client.get("/api/v1/studio-info")

    assert resp.status_code == 404


async def test_update_studio_info(client: AsyncClient, mock_db_conn):
    updated = {**_INFO_ROW, "students_count": 600}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, updated]

    resp = await client.patch(
        "/api/v1/studio-info",
        json={"students_count": 600},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["students_count"] == 600


async def test_update_studio_info_forbidden(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/studio-info",
        json={"students_count": 600},
    )

    assert resp.status_code == 401


async def test_update_studio_info_multiple_fields(client: AsyncClient, mock_db_conn):
    updated = {**_INFO_ROW, "phone": "+7 (000) 000-00-00", "address": "Новый адрес"}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, updated]

    resp = await client.patch(
        "/api/v1/studio-info",
        json={"phone": "+7 (000) 000-00-00", "address": "Новый адрес"},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["phone"] == "+7 (000) 000-00-00"
    assert resp.json()["address"] == "Новый адрес"
