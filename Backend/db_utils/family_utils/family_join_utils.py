
from family_crud_utils import *
from recipe_utils import authenticate_recipe_ownership

def _read_join_request(
    request_id: int,
    db: DbDependancy
):
    request = (
        db.query(models.RequestToJoinFamily)
        .filter(
            models.RequestToJoinFamily.id == request_id,
        )
        .first()
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Request to join family not found."
        )

    return request

def _remove_join_request(
    request_id: int,
    db: DbDependancy,
):
    existing_request = (
        db.query(models.RequestToJoinFamily)
        .filter(
            models.RequestToJoinFamily.id == request_id,
        )
        .first()
    )

    if existing_request is None:
        raise HTTPException(
            status_code=404,
            detail="Request to join family not found."
        )

    db.delete(existing_request)
    db.commit()

    return {"message": "Join Request Removed Sucessfully."}


def request_to_join_family(
    current_user_id: int,
    invite_code: str,
    db: DbDependancy,
):
    family = (
        db.query(models.Family)
        .filter(
            models.Family.invite_code == invite_code
        )
        .first()
    )

    if family is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid invite code."
        )

    try:
        existing_member = authenticate_family_member(
            current_user_id,
            family.id,
            db,
        )
    except HTTPException as e:
        if e.status_code == 404:
            existing_member = None
        else:
            raise

    if existing_member:
        raise HTTPException(
            status_code=409,
            detail="You are already a member of this family."
        )

    existing_request = (
        db.query(models.RequestToJoinFamily)
        .filter(
            models.RequestToJoinFamily.family_id == family.id,
            models.RequestToJoinFamily.user_id == current_user_id,
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=409,
            detail="You already have requested to join this family."
        )

    join_request = models.RequestToJoinFamily(
        user_id=current_user_id,
        family_id=family.id,
        requested_by=current_user_id,
    )

    db.add(join_request)
    db.commit()
    db.refresh(join_request)

    return join_request

def read_family_join_requests(
    current_user_id: int,
    family_id: int,
    db: DbDependancy,
) -> list[schemas.UserRead]:

    current_user = authenticate_family_member(
        current_user_id,
        family_id,
        db,
    )

    join_requests = (
        db.query(models.RequestToJoinFamily)
        .filter(
            models.RequestToJoinFamily.family_id == family_id,
        )
        .all()
    )

    users = []

    for request in join_requests:
        user = user_utils.read_user(
            request.user_id,
            db,
        )

        users.append(
            schemas.UserRead.model_validate(user)
        )

    return users

def deny_join_request(
    current_user_id: int,
    request_id: int,
    db: DbDependancy
):
    request = _read_join_request(request_id, db)
    is_family_member_admin(current_user_id, request.family_id, db)
    _remove_join_request(request_id, db)

    return {"message": "Join Request Removed Sucessfully."}

def remove_own_join_request(
    current_user_id: int,
    request_id: int,
    db: DbDependancy,     
):
    request = _read_join_request(request_id, db)
    
    if request.user_id != current_user_id:
        raise HTTPException(
            status_code=405,
            detail="Cannot remove others join requests."
        )

    _remove_join_request(request_id, db)
    return {"message": "Join Request Removed Sucessfully."}

def approve_join_request(
    current_user_id: int,
    request_id: int,
    new_family_member_role: schemas.FamilyMemberRole,
    db: DbDependancy  
):
    request = _read_join_request(request_id, db)
    is_family_member_admin(current_user_id, request.family_id, db)
    add_member_to_family(current_user_id, request.user_id, request.family_id, new_family_member_role, db)

    return {"message": "Join Request Approved Sucessfully."}