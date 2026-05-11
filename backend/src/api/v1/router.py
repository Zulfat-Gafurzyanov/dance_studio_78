from fastapi import APIRouter

from src.api.v1.admin import router as admin_router
from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.price import router as price_router
from src.api.v1.schedule import router as schedule_router
from src.api.v1.studioinfo import router as studioinfo_router
from src.api.v1.style import router as style_router
from src.api.v1.teacher import router as teacher_router
from src.api.v1.users import router as users_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(admin_router)
v1_router.include_router(style_router)
v1_router.include_router(teacher_router)
v1_router.include_router(price_router)
v1_router.include_router(studioinfo_router)
v1_router.include_router(schedule_router)
