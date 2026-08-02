
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy
import schemas

def read_user(
        user_id: int,
        db: DbDependancy,
): 
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
    
    return user