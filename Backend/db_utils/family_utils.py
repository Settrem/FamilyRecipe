
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas

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

def authenticate_family_member(
    user_id: int,
    family_id: int, 
    db: DbDependancy,
) -> models.FamilyMember:

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
            detail="Family member not found."
        )
    
    return family_member

#This function lets us add new members to the family (cannot be given role of creator)
def add_member_to_family(
        user_id: int,
        family_id: int,
        new_family_member_role: models.FamilyMemberRole,
        db: DbDependancy,
):

    if new_family_member_role == models.FamilyMemberRole.Creator:
        raise HTTPException(
            status_code=405,
            detail="Not allowed to add a user as Creator"
        )

    #Query for the family and user to make sure they exist
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

    user = (
        db.query(models.User)
        .filter(
            models.User.id == user_id,
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    #Query if user already is in the family
    user_in_family = (
        db.query(models.FamilyMember)
        .filter(
            models.FamilyMember.user_id == user_id,
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
        user_id=user_id,
        family_member_role= new_family_member_role,
    )

    db.add(new_family_member)
    db.commit()

    