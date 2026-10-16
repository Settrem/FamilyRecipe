from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated

import schemas
import auth
import models

from database import DbDependancy
from db_utils import family_request_utils


router = APIRouter(
    prefix="/current_user/",
    tags=["Family Join Requests"]
)


# POST /current_user/family/join-request
# Sends a request to join a family using its invite code.
@router.post(
    "/family/join-request",
)
def request_to_join_family(
    invite_code: str,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.request_to_join_family(
        current_user_id=current_user.id,
        invite_code=invite_code,
        db=db,
    )


# GET /current_user/family/{family_id}/join-request
# Gets all users who have requested to join the specified family.
@router.get(
    "/family/{family_id}/join-request",
    response_model=list[schemas.UserRead],
)
def get_family_join_requests(
    family_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.read_family_join_requests(
        current_user_id=current_user.id,
        family_id=family_id,
        db=db,
    )


# DELETE /current_user/family/join-request/{request_id}
# Denies a join request. Only a family admin can perform this action.
@router.delete(
    "/family/join-request/{request_id}",
)
def deny_join_request(
    request_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.deny_join_request(
        current_user_id=current_user.id,
        request_id=request_id,
        db=db,
    )


# DELETE /current_user/family/my-join-request/{request_id}
# Removes a join request created by the current user.
@router.delete(
    "/family/my-join-request/{request_id}",
)
def remove_own_join_request(
    request_id: int,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.remove_own_join_request(
        current_user_id=current_user.id,
        request_id=request_id,
        db=db,
    )


# POST /current_user/family/join-request/{request_id}/approve
# Approves a join request and adds the user to the family with the selected role.
@router.post(
    "/family/join-request/{request_id}/approve",
)
def approve_join_request(
    request_id: int,
    new_family_member_role: schemas.FamilyMemberRole,
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.approve_join_request(
        current_user_id=current_user.id,
        request_id=request_id,
        new_family_member_role=new_family_member_role,
        db=db,
    )

# GET /current_user/family/join-request
# Gets all families that the current user has requested to join.
@router.get(
    "/family/join-request",
    response_model=list[schemas.FamilyRead],
)
def get_own_join_requests(
    current_user: Annotated[
        models.User,
        Depends(auth.get_current_user),
    ],
    db: DbDependancy,
):
    return family_request_utils.read_own_join_requests(
        current_user_id=current_user.id,
        db=db,
    )