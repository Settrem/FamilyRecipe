
from db_utils.family_utils.family_crud_utils import *

# Check if recipe is shared in family
def _is_recipe_shared(
    family_id: int,
    recipe_id: int,
    db: DbDependancy,
) -> bool:
    existing = (
        db.query(models.FamilyRecipe)
        .filter(
            models.FamilyRecipe.family_id == family_id,
            models.FamilyRecipe.recipe_id == recipe_id,
        )
        .first()
    )

    if existing:
        return True

    return False

def add_recipe_to_family(
    current_user_id: int,
    family_id: int,
    recipe_id: int,
    db: DbDependancy,
):

    # Check user belongs to family and can edit family
    deny_viewer_to_edit(
        current_user_id,
        family_id,
        db,
    )

    # Check recipe ownership
    recipe = authenticate_recipe_ownership(current_user_id, recipe_id, db)

    # Check if already shared
    existing = _is_recipe_shared(family_id, recipe_id, db)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Recipe is already shared with this family."
        )

    family_recipe = models.FamilyRecipe(
        family_id=family_id,
        recipe_id=recipe_id,
    )

    db.add(family_recipe)
    db.commit()
    db.refresh(family_recipe)

    return family_recipe

# Here you can get all recipes shared with a family
def read_family_recipes(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
):

    authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    recipes = (
        db.query(models.Recipe)
        .join(
            models.FamilyRecipe,
            models.Recipe.id == models.FamilyRecipe.recipe_id
        )
        .filter(
            models.FamilyRecipe.family_id == family_id
        )
        .all()
    )

    return recipes

#Here you can get all recipes shared by a specific family member
def read_family_member_recipes(
    current_user_id: int,
    family_id: int,
    family_member_id: int,
    db: DbDependancy,
):

    family_member = read_family_member(current_user_id, family_member_id, db)

    recipes = (
        db.query(models.Recipe)
        .join(
            models.FamilyRecipe,
            models.Recipe.id == models.FamilyRecipe.recipe_id
        )
        .filter(
            models.FamilyRecipe.family_id == family_id,
            models.Recipe.author_id == family_member.user_id,
        )
        .all()
    )

    return recipes


def remove_recipe_from_family(
    current_user_id: int,
    family_id: int,
    recipe_id: int,
    db: DbDependancy,
):

    deny_viewer_to_edit(
        current_user_id,
        family_id,
        db,
    )

    family_recipe = (
        db.query(models.FamilyRecipe)
        .join(
            models.Recipe,
            models.Recipe.id == models.FamilyRecipe.recipe_id
        )
        .filter(
            models.FamilyRecipe.family_id == family_id,
            models.FamilyRecipe.recipe_id == recipe_id,
            models.Recipe.author_id == current_user_id,
        )
        .first()
    )

    if family_recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found or you are not the owner."
        )

    db.delete(family_recipe)
    db.commit()

    return {
        "message": "Recipe removed from family."
    }

def remove_member_recipe_from_family(
    current_user_id: int,
    family_id: int,
    recipe_id: int,
    db: DbDependancy,
):

    family_member = is_family_member_admin(
        current_user_id,
        family_id,
        db,
    )

    family_recipe = (
        db.query(models.FamilyRecipe)
        .filter(
            models.FamilyRecipe.family_id == family_id,
            models.FamilyRecipe.recipe_id == recipe_id,
        )
        .first()
    )

    if family_recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe is not shared with this family."
        )


    db.delete(family_recipe)
    db.commit()

    return {
        "message": "Recipe removed from family."
    }


def preview_family_recipes(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
) -> list[schemas.RecipePreviewInFamily]:

    # Check user belongs to family
    authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    recipes = (
        db.query(models.Recipe)
        .join(
            models.FamilyRecipe,
            models.Recipe.id == models.FamilyRecipe.recipe_id
        )
        .join(
            models.User,
            models.Recipe.author_id == models.User.id
        )
        .filter(
            models.FamilyRecipe.family_id == family_id
        )
        .all()
    )

    return [
        schemas.RecipePreviewInFamily(
            id=recipe.id,
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            step_count=len(recipe.recipe_instructions or []),
            ingredient_count=len(recipe.ingredients or []),
            recipe_creator=f"{recipe.author.first_name} {recipe.author.last_name}"
        )
        for recipe in recipes
    ]

def preview_family_member_recipes(
    current_user_id: int,
    family_id: int,
    family_member_id: int,
    db: DbDependancy,
) -> list[schemas.RecipePreviewInFamily]:

    family_member = read_family_member(current_user_id, family_member_id, db)

    recipes = (
        db.query(models.Recipe)
        .join(
            models.FamilyRecipe,
            models.Recipe.id == models.FamilyRecipe.recipe_id
        )
        .join(
            models.User,
            models.Recipe.author_id == models.User.id
        )
        .filter(
            models.FamilyRecipe.family_id == family_id,
            models.Recipe.author_id == family_member.user_id,
        )
        .all()
    )

    return [
        schemas.RecipePreviewInFamily(
            id=recipe.id,
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            step_count=len(recipe.recipe_instructions or []),
            ingredient_count=len(recipe.ingredients or []),
            recipe_creator=f"{recipe.author.first_name} {recipe.author.last_name}"
        )
        for recipe in recipes
    ]