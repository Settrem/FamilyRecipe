from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

import schemas
import auth
import models

from database import DbDependancy
from db_utils import recipe_utils


router = APIRouter(
    prefix="/current_user",
    tags=["Recipes"]
)

#To create a recipe use url POST /current_user/recipe
@router.post(
    "/recipe",
    response_model=schemas.RecipeRead,
)
def create_recipe(
    recipe: schemas.RecipeCreate,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,   
):
    return recipe_utils.create_recipe(
        user_id=current_user.id,
        recipe=recipe,
        recipe_status=models.RecipeStatus.Not_Finished,
        db=db,
    )

@router.get(
    "/recipe",
    response_model=list[schemas.RecipePreview],
)
def get_recipe(
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return recipe_utils.preview_recipes_of_user(
        user_id=current_user.id,
        db=db,
    )

@router.get(
    "/recipe/{recipe_id}",
    response_model=schemas.RecipeRead,
)
def get_recipe(
    recipe_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return recipe_utils.get_recipe_of_user(
        recipe_id=recipe_id,
        user_id=current_user.id,
        db=db,
    )

#PATCH  /current_user/recipe/{recipe_id} 
#We use patch as we only send the variables we want to update and not the entire recipe with some changed values
@router.patch(
    "/recipe/{recipe_id}",
    response_model=schemas.RecipeRead,
)
def update_recipe(
    recipe_id: int,
    recipe_update: schemas.RecipeUpdate,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return recipe_utils.update_recipe(
        recipe_id=recipe_id,
        user_id=current_user.id,
        recipe_update=recipe_update,
        db=db,
    )

#DELETE /current_user/recipe/{recipe_id}
#This is used so a user can delete one of their recipes
#The recipe util function already checks ownership so it has RLS
@router.delete("/recipe/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return recipe_utils.delete_recipe(
        recipe_id=recipe_id,
        user_id=current_user.id,
        db=db,
    )
