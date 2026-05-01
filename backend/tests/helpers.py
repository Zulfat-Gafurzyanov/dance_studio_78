import src.core.security as security

_USER_ROW = {
    "id": 99,
    "email": "user@example.com",
    "is_active": True,
    "role": "user",
    "created_at": "2025-01-01T00:00:00Z",
}

_ADMIN_ROW = {
    "id": 1,
    "email": "admin@example.com",
    "is_active": True,
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
}


def _admin_token(user_id: int = 1) -> dict:
    token = security.create_access_token(user_id, "admin")
    return {"Authorization": f"Bearer {token}"}


def _user_token(user_id: int = 1, role: str = "user") -> dict:
    token = security.create_access_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}
