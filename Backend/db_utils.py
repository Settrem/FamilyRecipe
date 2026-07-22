
#Import from own files
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
from database import DbDependancy

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
    