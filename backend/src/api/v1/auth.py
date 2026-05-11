from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response, status

from src.api.deps import get_auth_service
from src.schemas.auth import AccessTokenResponse, SignInRequest, SignUpRequest
from src.service.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 дней


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/v1/auth",
    )


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(
    response: Response,
    request: Annotated[SignUpRequest, Body],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AccessTokenResponse:
    tokens = await auth_service.sign_up(request)
    _set_refresh_cookie(response, tokens.refresh_token)
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/sign-in")
async def sign_in(
    response: Response,
    request: SignInRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AccessTokenResponse:
    tokens = await auth_service.sign_in(request)
    _set_refresh_cookie(response, tokens.refresh_token)
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/refresh")
async def refresh(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AccessTokenResponse:
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token отсутствует")
    tokens = await auth_service.refresh(refresh_token)
    _set_refresh_cookie(response, tokens.refresh_token)
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
