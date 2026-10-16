from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import hashlib

from typing import Annotated

import models
from database import DbDependancy

from env import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)

def normalize_password(password: str) -> bytes:
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    return password.encode("utf-8")

def hash_password(password: str) -> str:
    pw = normalize_password(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    pw = normalize_password(password)
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))

# ---- JWT ----
def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: DbDependancy,
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(models.User)
        .filter(
            models.User.email == email
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user

