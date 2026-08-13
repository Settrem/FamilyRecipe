from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends

from database import DbDependancy
import schemas
from models import RecipeStatus, FamilyMemberRole
from main import get_current_user


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)

@router.post("/")
def create_recipe(
    recipe: schemas.RecipeCreate,
    current_user: schemas.UserRead = Depends(get_current_user),
    db: DbDependancy = Depends(),
):
    return create_recipe(
        user_id=current_user.id,
        recipe=recipe,
        recipe_status=RecipeStatus.Not_Finished,
        db=db,
    )