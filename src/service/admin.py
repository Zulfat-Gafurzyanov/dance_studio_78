from src.schemas.user import UserProfile
from src.service.user import UserService


class AdminService:
    def __init__(self, user_service: UserService):
        self.users = user_service

# ===== ПОЛЬЗОВАТЕЛИ =====

    async def get_user(self, user_id: int) -> UserProfile:
        return await self.users.get_profile(user_id)

    async def get_all_users(
        self, limit: int = 50, offset: int = 0
    ) -> list[UserProfile]:
        return await self.users.get_all(limit, offset)

    async def set_active(self, user_id: int, is_active: bool) -> UserProfile:
        return await self.users.set_active(user_id, is_active)

    async def set_role(self, user_id: int, role: str) -> UserProfile:
        return await self.users.set_role(user_id, role)
