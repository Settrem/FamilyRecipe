
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas
import user_utils
from recipe_utils import authenticate_recipe_ownership
import secrets
import string

####
# invite code generations
####

def generate_invite_code(length: int = models.INVITE_CODE_LENGTH) -> str:
    #we avoid similar looking characters
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

#This function is used to create a unique 16 char invite code with a maximum of 5 rollbacks (unlikely to happen)
def create_unique_invite_code(
    db: DbDependancy,
    length: int = 16,
) -> str:

    for _ in range(5):
        code = generate_invite_code(length)

        existing = (
            db.query(models.Family)
            .filter(models.Family.invite_code == code)
            .first()
        )

        if existing is None:
            return code

    raise HTTPException(
        status_code=500,
        detail="Could not generate a unique invite code."
    )

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

#This function creates a family with the creator as the first member and role creator
def create_family(
    current_user_id: int,
    family: schemas.FamilyCreate,
    db: DbDependancy,
):
    new_family = models.Family(
        creator=current_user_id,
        title=family.title,
        description=family.description,
        invite_code=create_unique_invite_code(db),
    )

    db.add(new_family)
    db.flush()

    family_member = models.FamilyMember(
        family_id=new_family.id,
        user_id=current_user_id,
        family_member_role=models.FamilyMemberRole.Creator,
    )

    db.add(family_member)
    db.commit()
    db.refresh(new_family)

    return new_family

#Checks if a user is a member of a family
def authenticate_family_member(
    current_user_id: int,
    family_id: int, 
    db: DbDependancy,
) -> models.FamilyMember:

    #Query for the user
    user = user_utils.read_user(current_user_id, db)

    #Query for the family
    family = _read_family(family_id, db)

    #Query for the family member
    family_member = (
        db.query(models.FamilyMember)
        .filter(
            models.FamilyMember.family_id == family_id,
            models.FamilyMember.user_id == current_user_id,
        ).first()
    )

    if family_member is None:
        raise HTTPException(
            status_code=404,
            detail="User is not member of Family."
        )
    
    return family_member

#Authenticate the user, Check they're a member of the family, Return the family.
def read_family(
    user_id: int,
    family_id: int,
    db: DbDependancy,
):
    authenticate_family_member(
        user_id,
        family_id,
        db,
    )

    family = _read_family(family_id, db)

    members = []

    for member in family.members:
        user = user_utils.read_user(member.user_id, db)

        members.append(
            schemas.FamilyMemberRead(
                user_id=member.user_id,
                family_member_role=member.family_member_role,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        )

    recipes = []

    for family_recipe in family.family_recipes:
        recipe = family_recipe.recipe

        recipes.append(
            schemas.RecipePreviewInFamily(
                id=recipe.id,
                title=recipe.title,
                cooking_time=recipe.cooking_time,
                step_count=len(recipe.recipe_instructions),
                ingredient_count=len(recipe.ingredients),
                recipe_creator=(
                    f"{recipe.author.first_name} "
                    f"{recipe.author.last_name}"
                ),
            )
        )

    return schemas.FamilyRead(
        id=family.id,
        creator=family.creator,
        title=family.title,
        description=family.description,
        invite_code=family.invite_code,
        members=members,
        recipes=recipes,
    )

#This function checks if a user has the admin class or the classes above
def is_family_member_admin(
    current_user_id: int,
    family_id: int,
    db: DbDependancy
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

    return current_user

#This function denys a user with role visitor do edit inside family
def deny_viewer_to_edit(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
):

    # Verify that the current user belongs to the same family
    current_user = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )
    
    if current_user.family_member_role not in (
        models.FamilyMemberRole.Editor,
        models.FamilyMemberRole.Administrator,
        models.FamilyMemberRole.Creator,
    ):
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to edit family."
        )

    return current_user
    
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
    current_user = is_family_member_admin(
        current_user_id,
        family_id,
        db,
    )

    if new_family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=405,
            detail="Not allowed to add a user as Creator"
        )

    #Query for the family and user to make sure they exist
    family = _read_family(family_id, db)

    user_to_add = user_utils.read_user(user_to_add_id, db)

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

    if family_member.family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=403,
            detail="The Creator's role cannot be changed."
        )

    # Verify that the current user belongs to the same family
    current_user = is_family_member_admin(
        current_user_id,
        family_member.family_id,
        db,
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

    # Verify that the current user has admin permission
    current_user = is_family_member_admin(
        current_user_id,
        family_member_to_delete.family_id,
        db,
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


def update_family(
    current_user_id: int,
    family_id: int,
    family_update: schemas.FamilyUpdate,
    db: DbDependancy,
):
    current_user = is_family_member_admin(
        current_user_id,
        family_id,
        db,
    )

    family = _read_family(
        family_id,
        db,
    )

    update_data = family_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(family, key, value)

    db.commit()
    db.refresh(family)

    return family
