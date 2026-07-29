from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, TypeAlias
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

#Import from own files
from database import Base, engine, SessionLocal, DbDependancy
import models
import auth
import schemas
import Backend.db_utils.recipe_utils as recipe_utils

Base.metadata.create_all(bind=engine)
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#FastAPI automatically returns a 422 Unprocessable Entity if parameters are wrong types
@app.post("/signup")
def signup(user: schemas.UserCreate, db: DbDependancy):

    existing = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    new_user = models.User(
        email=user.email,
        password_hash=auth.hash_password(user.password),
        first_name= user.first_name,
        last_name= user.last_name,
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


@app.post("/token", response_model=schemas.Token)
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
            models.User.email == form_data.username
        )
        .first()
    )

    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not auth.verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_access_token(
        {"sub": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

#This function does all the authentication work, you can then use it as a dependancy like: current_user: Annotated[User, Depends(get_current_user)], 
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDependancy,
):

    try:
        payload = jwt.decode(
            token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM],
        )

        email = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user

@app.get("/current_user/")
def me(
    db_user: Annotated[
        models.User,
        Depends(get_current_user),
    ],
):
    return {
        "message": "User created successfully",
        "id": db_user.id,
        "firstname": db_user.first_name,
        "lastname": db_user.last_name,
        "email": db_user.email,
        "disabled": db_user.disabled,
    }

#By not giving user id to get recipes, we restrict the user from only getting recepies of the logged in user
@app.get("/current_user/recepies", response_model=list[schemas.Recipe])
async def get_users_receipe(
    current_user:  Annotated[models.User, Depends(get_current_user)],
): 
    return recipe_utils.get_recipes_of_user(current_user.id)
