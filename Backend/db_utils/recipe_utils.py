
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas
from models import RecipeStatus, FamilyMemberRole

#This function returns all the recipes of a user in their entirety
def get_recipes_of_user(
    user_id: int,
    db: DbDependancy,
):
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.user_id == user_id)
        .all()
    )

    if recipes is None:
        raise HTTPException(
            status_code=404,
            detail="No receipies",
        )

    return recipes

# Returns a single recipe only if the given user owns it.
def get_recipe_of_user(
    recipe_id: int,
    user_id: int,
    db: DbDependancy,
):
    recipe = (
        db.query(models.Recipe)
        .filter(
            models.Recipe.id == recipe_id,
            models.Recipe.author_id == user_id,
        )
        .first()
    )

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found, or user not owner of recipe."
        )

    return recipe

#This function returns all the recipes of a user in a preview format so we dont have to send as much data to online users
def preview_recipes_of_user(
    user_id: int,
    db: DbDependancy,
) -> list[schemas.RecipePreview]:
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.author_id == user_id)
        .all()
    )

    return [
        schemas.RecipePreview(
            id=recipe.id,
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            step_count=len(recipe.recipe_instructions or []),
            ingredient_count=len(recipe.ingredients or []),
        )
        for recipe in recipes
    ]

# This function is used to add a new recipe to the database
# The parameters are the user id of the recipe creator, the recipe, and the status os the recipe which fillows the RecipeStatus type
def create_recipe(
    user_id: int,
    recipe: schemas.RecipeCreate,
    recipe_status: RecipeStatus,
    db: DbDependancy,
):
    new_recipe = models.Recipe(
        author_id=user_id,
        title=recipe.title,
        description=recipe.description,
        cooking_time=recipe.cooking_time,
        portion_amount=recipe.portion_amount,
        ingredients=[ingredient.model_dump() for ingredient in recipe.ingredients],
        recipe_instructions=[
            step.model_dump() for step in recipe.recipe_instructions
        ],
        status=recipe_status,
    )

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return new_recipe

#This function updates the recipe of the given recipe id, the user_id makes sure users can only edit their own recipe
def update_recipe(
    recipe_id: int,
    user_id: int,
    recipe_update: schemas.RecipeUpdate,
    db: DbDependancy,
):
    #Query for the recipe
    recipe = get_recipe_of_user(
        recipe_id=recipe_id,
        user_id=user_id,
        db=db,
    )

    # Get only fields that were provided using exclude_unset=true
    update_data = recipe_update.model_dump(exclude_unset=True)

    if "ingredients" in update_data:
        update_data["ingredients"] = [
            ingredient.model_dump()
            for ingredient in recipe_update.ingredients
        ]

    if "recipe_instructions" in update_data:
        update_data["recipe_instructions"] = [
            step.model_dump()
            for step in recipe_update.recipe_instructions
        ]

    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)

    return recipe

#This function verifies the user and deletes the given recipe
def delete_recipe(
    recipe_id: int,
    user_id: int,
    db: DbDependancy, 
):
    #Query for the recipe
    recipe = get_recipe_of_user(
        recipe_id=recipe_id,
        user_id=user_id,
        db=db,
    )

    db.delete(recipe)
    db.commit()

    return {"message": "Recipe deleted successfully."}

