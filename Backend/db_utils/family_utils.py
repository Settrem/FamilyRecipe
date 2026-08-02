
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas
from user_utils import *
from recipe_utils import authenticate_recipe_ownership

####
# Private Functions
####

def _read_family(
    family_id: int,
    db: DbDependancy,
):
    #Query for the family
    family = (
        db.query(models.Family)
        .filter(
            models.Family.id == family_id,
        )
        .first()
    )

    if family is None:
        raise HTTPException(
            status_code=404,
            detail="Family not found."
        )

    return family

def _read_family_member(
    family_member_id: int,
    db: DbDependancy,
):
    #Query for the family member
    family_member = (
        db.query(models.FamilyMember)
        .filter(
            models.FamilyMember.id == family_member_id,
        ).first()
    )

    if family_member is None:
        raise HTTPException(
            status_code=404,
            detail="Family member not found."
        )

    return family_member


####
# CRUD Functions
####

def create_family(
    user_id: int,
    family: schemas.FamilyCreate,
    db: DbDependancy,
):
    new_family = models.Family(
        creator=user_id,
        title=family.title,
        description=family.description,
    )

    db.add(new_family)
    db.flush()  # This gets the generated family.id without committing yet :)))

    family_member = models.FamilyMember(
        family_id=new_family.id,
        user_id=user_id,
        family_member_role=models.FamilyMemberRole.Creator,
    )

    db.add(family_member)
    db.commit()

    return new_family

#Checks if a user is a member of a family
def authenticate_family_member(
    user_id: int,
    family_id: int, 
    db: DbDependancy,
) -> models.FamilyMember:

    #Query for the user
    user = read_user(user_id, db)

    #Query for the family
    family = _read_family(family_id, db)

    #Query for the family member
    family_member = (
        db.query(models.FamilyMember)
        .filter(
            models.FamilyMember.family_id == family_id,
            models.FamilyMember.user_id == user_id,
        ).first()
    )

    if family_member is None:
        raise HTTPException(
            status_code=404,
            detail="User is not member of Family."
        )
    
    return family_member

def read_family_member(
    current_user_id: int,
    family_member_id: int,
    db: DbDependancy,
):
    #Query for the family member
    family_member = _read_family_member(family_member_id, db)

    # Verify that the current user belongs to the same family
    authenticate_family_member(
        current_user_id,
        family_member.family_id,
        db,
    )
    
    return family_member

def read_all_family_members(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
) -> list[schemas.FamilyMemberRead]:

    # Verify that the current user belongs to the family
    authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    # Query all family members
    family_members = (
        db.query(models.FamilyMember)
        .filter(models.FamilyMember.family_id == family_id)
        .all()
    )

    return family_members

#This function lets us add new members to the family (cannot be given role of creator)
def add_member_to_family(
        current_user_id: int,
        user_to_add_id: int,
        family_id: int,
        new_family_member_role: models.FamilyMemberRole,
        db: DbDependancy,
):

    # Verify that the current user belongs to the same family
    current_user = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )
    
    if current_user.family_member_role not in (
        models.FamilyMemberRole.Administrator,
        models.FamilyMemberRole.Creator,
    ):
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to add user to family."
        )

    if new_family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=405,
            detail="Not allowed to add a user as Creator"
        )

    #Query for the family and user to make sure they exist
    family = _read_family(family_id, db)

    user_to_add = read_user(user_to_add_id, db)

    #Query if user already is in the family
    user_in_family = (
        db.query(models.FamilyMember)
        .filter(
            models.FamilyMember.user_id == user_to_add.id,
            models.FamilyMember.family_id == family_id,
        )
        .first()
    )

    if user_in_family:
        raise HTTPException(
            status_code=404,
            detail="User is already part of this family."
        )

    new_family_member = models.FamilyMember(
        family_id=family.id,
        user_id=user_to_add.id,
        family_member_role= new_family_member_role,
    )

    db.add(new_family_member)
    db.commit()

# This function lets us change the role of members in the family
# (cannot be given the role of Creator or Removed)
def change_family_member_role(
    current_user_id: int,
    family_member_id: int,
    new_family_member_role: models.FamilyMemberRole,
    db: DbDependancy,
):
    if new_family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=405,
            detail="Not allowed to assign the Creator role."
        )

    #Read family member
    family_member = _read_family_member(family_member_id, db)

    # Verify that the current user belongs to the same family
    current_user = authenticate_family_member(
        current_user_id,
        family_member.family_id,
        db,
    )
    
    if current_user.family_member_role not in (
        models.FamilyMemberRole.Administrator,
        models.FamilyMemberRole.Creator,
    ):
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to add user to family."
        )

    family_member.family_member_role = new_family_member_role

    db.commit()
    db.refresh(family_member)

    return family_member


def delete_family_member(
    current_user_id: int,
    family_member_id_to_delete: int,
    db: DbDependancy, 
):
    
    #Query for the family member to be deleted
    family_member_to_delete = _read_family_member(family_member_id_to_delete, db)
    
    if family_member_to_delete.family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=405,
            detail="Not allowed to delete the Creator."
        )

    # Verify that the current user belongs to the same family
    current_user = authenticate_family_member(
        current_user_id,
        family_member_id_to_delete,
        db,
    )
    
    if current_user.family_member_role not in (
        models.FamilyMemberRole.Administrator,
        models.FamilyMemberRole.Creator,
    ):
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to add user to family."
        )
    
    if current_user.id == family_member_to_delete.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot remove yourself."
        )

    db.delete(family_member_to_delete)
    db.commit()

    return {"message": "Family Member removed successfully."}


def exit_family(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
):

    family_member = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    # Creator cannot leave if other members still exist
    if family_member.family_member_role == models.FamilyMemberRole.Creator:
            raise HTTPException(
                status_code=400,
                detail="You cannot quit as creator."
            )

    db.delete(family_member)
    db.commit()

    return {"message": "User exited family successfully."}

#This function lets you delete the entire family, this can only be done by the creator
def delete_family(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
):
    family_member = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    if family_member.family_member_role != models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to delete the family."
        )

    family = _read_family(family_id, db)

    # Delete all family members
    (
        db.query(models.FamilyMember)
        .filter(models.FamilyMember.family_id == family_id)
        .delete(synchronize_session=False)
    )

    # Delete the family
    db.delete(family)
    db.commit()

    return {"message": "Family deleted successfully."}


####
# Family Recipe Utils
####

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

    # Check user belongs to family
    authenticate_family_member(
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
def get_family_recipes(
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
def get_family_member_recipes(
    current_user_id: int,
    family_id: int,
    member_id: int,
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
            models.FamilyRecipe.family_id == family_id,
            models.Recipe.author_id == member_id,
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

    authenticate_family_member(
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

    family_member = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    if family_member.family_member_role not in (
        models.FamilyMemberRole.Creator,
        models.FamilyMemberRole.Administrator,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to remove recipes."
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
    member_id: int,
    db: DbDependancy,
) -> list[schemas.RecipePreviewInFamily]:

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
            models.FamilyRecipe.family_id == family_id,
            models.Recipe.author_id == member_id,
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