from httpx import AsyncClient

from tests.helpers import _ADMIN_ROW, _admin_token

_TEACHER_JOIN_ROW = {
    "teacher_id": 1,
    "name": "Анна Иванова",
    "bio": "Преподаватель балета",
    "is_active": True,
    "teacher_sort_order": 0,
    "photo_id": None,
    "url": None,
    "sort_order": None,
}

_TEACHER_CREATE_ROW = {
    "id": 1,
    "name": "Анна Иванова",
    "bio": "Преподаватель балета",
    "is_active": True,
}

_PHOTO_ROW = {
    "photo_id": 10,
    "url": "https://example.com/photo.jpg",
    "sort_order": 1,
}


async def test_get_all_teachers(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_TEACHER_JOIN_ROW]

    resp = await client.get("/api/v1/teachers")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Анна Иванова"


async def test_get_all_teachers_empty(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/teachers")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_teacher_by_id(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = [_TEACHER_JOIN_ROW]

    resp = await client.get("/api/v1/teachers/1")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Анна Иванова"


async def test_get_teacher_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetch.return_value = []

    resp = await client.get("/api/v1/teachers/999")

    assert resp.status_code == 404


async def test_create_teacher(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _TEACHER_CREATE_ROW]

    resp = await client.post(
        "/api/v1/teachers",
        json={"name": "Анна Иванова", "bio": "Преподаватель балета"},
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Анна Иванова"


async def test_create_teacher_forbidden(client: AsyncClient):
    resp = await client.post(
        "/api/v1/teachers",
        json={"name": "Анна Иванова", "bio": "Преподаватель балета"},
    )

    assert resp.status_code == 401


async def test_update_teacher(client: AsyncClient, mock_db_conn):
    updated_join = {**_TEACHER_JOIN_ROW, "name": "Анна Петрова"}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.side_effect = [[_TEACHER_JOIN_ROW], [updated_join]]

    resp = await client.patch(
        "/api/v1/teachers/1",
        json={"name": "Анна Петрова"},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Анна Петрова"


async def test_update_teacher_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.patch(
        "/api/v1/teachers/999",
        json={"name": "Кто-то"},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_teacher(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 1}]
    mock_db_conn.fetch.return_value = [_TEACHER_JOIN_ROW]

    resp = await client.delete("/api/v1/teachers/1", headers=_admin_token())

    assert resp.status_code == 204


async def test_delete_teacher_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW
    mock_db_conn.fetch.return_value = []

    resp = await client.delete("/api/v1/teachers/999", headers=_admin_token())

    assert resp.status_code == 404


async def test_add_photo(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, _PHOTO_ROW]
    mock_db_conn.fetch.return_value = [_TEACHER_JOIN_ROW]

    resp = await client.post(
        "/api/v1/teachers/1/photos",
        json={"url": "https://example.com/photo.jpg", "sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 201
    assert resp.json()["url"] == "https://example.com/photo.jpg"


async def test_update_photo(client: AsyncClient, mock_db_conn):
    updated_photo = {**_PHOTO_ROW, "sort_order": 5}
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, updated_photo]

    resp = await client.patch(
        "/api/v1/teachers/photos/10",
        json={"sort_order": 5},
        headers=_admin_token(),
    )

    assert resp.status_code == 200
    assert resp.json()["sort_order"] == 5


async def test_update_photo_not_found(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, None]

    resp = await client.patch(
        "/api/v1/teachers/photos/999",
        json={"sort_order": 1},
        headers=_admin_token(),
    )

    assert resp.status_code == 404


async def test_delete_photo(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.side_effect = [_ADMIN_ROW, {"id": 10}]

    resp = await client.delete(
        "/api/v1/teachers/photos/10", headers=_admin_token()
    )

    assert resp.status_code == 204


async def test_reorder_teachers(client: AsyncClient, mock_db_conn):
    mock_db_conn.fetchrow.return_value = _ADMIN_ROW

    resp = await client.post(
        "/api/v1/teachers/reorder",
        json=[{"id": 1, "sort_order": 1}, {"id": 2, "sort_order": 2}],
        headers=_admin_token(),
    )

    assert resp.status_code == 204
