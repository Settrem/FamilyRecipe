
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas
from user_utils import *

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




