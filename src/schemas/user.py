import datetime as dt

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: dt.datetime


class UserUpdate(BaseModel):
    email: EmailStr | None = None
