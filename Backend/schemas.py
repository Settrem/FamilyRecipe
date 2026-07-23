
from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    disabled: bool

    model_config = {
        "from_attributes": True
    }

class CreateRecipe(BaseModel):
    id: int
    recipe_name: str 
    creator_id: int