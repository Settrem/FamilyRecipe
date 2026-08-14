from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

import schemas
import auth
import models

from database import DbDependancy
from db_utils import user_utils


router = APIRouter(
    prefix="/current_user",
    tags=["Users"],
)

@router.get("/")
def me(
    db_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
):
    return {
        "message": "User retrieved successfully",
        "id": db_user.id,
        "firstname": db_user.first_name,
        "lastname": db_user.last_name,
        "email": db_user.email,
        "disabled": db_user.disabled,
    }