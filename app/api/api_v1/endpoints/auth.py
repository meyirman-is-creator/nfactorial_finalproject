from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import user
from app.schemas.auth import Token, LoginRequest

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user_obj = user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user_obj:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user_obj.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/json", response_model=Token)
def login_access_token_json(
        login_data: LoginRequest,
        db: Session = Depends(get_db),
) -> Any:
    """
    Login using JSON request body.
    """
    user_obj = user.authenticate(db, email=login_data.email, password=login_data.password)
    if not user_obj:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user_obj.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }