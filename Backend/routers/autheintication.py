from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import models
import schemas
import auth

from database import DbDependancy

router = APIRouter(
    prefix="",
    tags=["Authentication"],
)

@router.post("/signup")
def signup(
    user: schemas.UserCreate,
    db: DbDependancy,
):
    existing = (
        db.query(models.User)
        .filter(
            models.User.email == user.email
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    new_user = models.User(
        email=user.email,
        password_hash=auth.hash_password(
            user.password
        ),
        first_name=user.first_name,
        last_name=user.last_name,
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User created"
    }


@router.post(
    "/token",
    response_model=schemas.Token,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: DbDependancy,
):
    user = (
        db.query(models.User)
        .filter(
            models.User.email
            == form_data.username
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not auth.verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = auth.create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }