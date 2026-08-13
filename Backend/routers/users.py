from typing import Annotated

from fastapi import APIRouter, Depends

import models
import auth


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