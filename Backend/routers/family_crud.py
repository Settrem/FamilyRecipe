from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

import schemas
import auth
import models

from database import DbDependancy
from db_utils import family_utils, user_utils


router = APIRouter(
    prefix="/current_user/",
    tags=["Family"]
)

#To create a family use url POST /family
@router.post(
    "/family",
    response_model=schemas.FamilyRead,
)
def create_family(
    new_family: schemas.FamilyCreate,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy = Depends(),   
):
    return family_utils.create_family(
        user_id=current_user.id,
        family=new_family,
        db=db,
    )

@router.get(
    "/families",
    response_model=list[schemas.FamilyRead],
)
def get_families(
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return user_utils.read_users_families(
        user_id=current_user.id,
        db=db,
    )

@router.get(
    "/family/{family_id}",
    response_model=schemas.FamilyRead,
)
def get_family(   
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_utils.read_family(
        user_id=current_user.id,
        family_id=family_id,
        db=db, 
    )

@router.patch(
    "/family/{family_id}",
    response_model=schemas.FamilyRead,
)
def update_family(
    family_id: int,
    family_update: schemas.FamilyUpdate,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_utils.update_family(
        user_id=current_user.id,
        family_id=family_id,
        family_update=family_update,
        db=db,
    )

@router.delete("/family/{family_id}")
def delete_family(
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_utils.delete_family(
        user_id=current_user.id,
        family_id=family_id,
        db=db,
    )
