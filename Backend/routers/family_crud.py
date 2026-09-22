from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

from Backend.db_utils.family_utils import family_crud_utils
import schemas
import auth
import models

from database import DbDependancy
from db_utils import user_utils


router = APIRouter(
    prefix="/current_user/",
    tags=["Family"]
)


# Creates a new family with the current user as the creator
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
    return family_crud_utils.create_family(
        current_user_id=current_user.id,
        family=new_family,
        db=db,
    )


# Returns all families that the current user is a member of
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


# Returns a specific family if the current user is a member of it
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
    return family_crud_utils.read_family(
        user_id=current_user.id,
        family_id=family_id,
        db=db,
    )


# Updates the information of a family
# The user must have the required permissions to edit the family
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
    return family_crud_utils.update_family(
        user_id=current_user.id,
        family_id=family_id,
        family_update=family_update,
        db=db,
    )


# Deletes a family
# Only the creator is allowed to delete the family
@router.delete("/family/{family_id}")
def delete_family(
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_crud_utils.delete_family(
        user_id=current_user.id,
        family_id=family_id,
        db=db,
    )
