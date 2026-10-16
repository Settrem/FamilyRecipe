from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

import schemas
import auth
import models

from database import DbDependancy
from db_utils import family_recipe_utils

router = APIRouter(
    prefix="/current_user/",
    tags=["Family Recipes"]
)

# POST /current_user/family/{family_id}/recipe/{recipe_id}
# Shares one of the current user's recipes with a family.
@router.post(
    "/family/{family_id}/recipe/{recipe_id}",
)
def add_recipe_to_family(
    family_id: int,
    recipe_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.add_recipe_to_family(
        current_user_id=current_user.id,
        family_id=family_id,
        recipe_id=recipe_id,
        db=db,
    )


# GET /current_user/family/{family_id}/recipe
# Gets all recipes that have been shared with the family.
@router.get(
    "/family/{family_id}/recipe",
    response_model=list[schemas.RecipeRead],
)
def get_family_recipes(
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.read_family_recipes(
        current_user_id=current_user.id,
        family_id=family_id,
        db=db,
    )


# GET /current_user/family/{family_id}/recipe/preview
# Gets a preview of all recipes shared with the family.
@router.get(
    "/family/{family_id}/recipe/preview",
    response_model=list[schemas.RecipePreviewInFamily],
)
def get_family_recipe_previews(
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.preview_family_recipes(
        current_user_id=current_user.id,
        family_id=family_id,
        db=db,
    )


# GET /current_user/family/{family_id}/member/{family_member_id}/recipe
# Gets all recipes shared with the family that were created by a specific family member.
@router.get(
    "/family/{family_id}/member/{family_member_id}/recipe",
    response_model=list[schemas.RecipeRead],
)
def get_family_member_recipes(
    family_id: int,
    family_member_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.read_family_member_recipes(
        current_user_id=current_user.id,
        family_id=family_id,
        family_member_id=family_member_id,
        db=db,
    )


# GET /current_user/family/{family_id}/member/{family_member_id}/recipe/preview
# Gets previews of recipes shared with the family by a specific family member.
@router.get(
    "/family/{family_id}/member/{family_member_id}/recipe/preview",
    response_model=list[schemas.RecipePreviewInFamily],
)
def get_family_member_recipe_previews(
    family_id: int,
    family_member_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.preview_family_member_recipes(
        current_user_id=current_user.id,
        family_id=family_id,
        family_member_id=family_member_id,
        db=db,
    )


# DELETE /current_user/family/{family_id}/recipe/{recipe_id}
# Removes one of the current user's recipes from the family.
@router.delete(
    "/family/{family_id}/recipe/{recipe_id}",
)
def remove_recipe_from_family(
    family_id: int,
    recipe_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.remove_recipe_from_family(
        current_user_id=current_user.id,
        family_id=family_id,
        recipe_id=recipe_id,
        db=db,
    )


# DELETE /current_user/family/{family_id}/member/recipe/{recipe_id}
# Allows a family admin to remove a recipe from the family.
@router.delete(
    "/family/{family_id}/member/recipe/{recipe_id}",
)
def remove_member_recipe_from_family(
    family_id: int,
    recipe_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_recipe_utils.remove_member_recipe_from_family(
        current_user_id=current_user.id,
        family_id=family_id,
        recipe_id=recipe_id,
        db=db,
    )