from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.deps import get_db, get_redis
import src.core.security as security


@pytest.fixture
def mock_db_conn() -> AsyncMock:
    """Заглушка asyncpg-соединения."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchval = AsyncMock(return_value=None)
    conn.execute = AsyncMock(return_value="OK")
    return conn


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Заглушка Redis."""
    r = AsyncMock()
    r.ping = AsyncMock(return_value=True)
    r.get = AsyncMock(return_value=None)
    r.setex = AsyncMock()
    r.delete = AsyncMock(return_value=1)
    return r


@pytest.fixture
async def client(mock_db_conn, mock_redis)-> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент для тестов с замоканными БД и Redis."""
    from main import app
    
    async def override_get_db():
        yield mock_db_conn

    def override_get_redis():
        return mock_redis

    # Подменяем БД и Redis.
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Убираем подмены.
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def load_test_keys() -> None:
    """Генерирует тестовую RSA-пару и загружает её в security модуль."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    security._private_key = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ).decode()
    security._public_key = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()