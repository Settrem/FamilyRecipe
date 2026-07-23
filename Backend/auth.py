from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import hashlib
from .env import SECRET_KEY, ALGORITHM ,ACCESS_TOKEN_EXPIRE_MINUTES

# ANVÄND BCVRYPT ISTÄLLET FÖR PASSLIB


#Läs mer på https://fastapi.tiangolo.com/tutorial/security/first-steps/

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