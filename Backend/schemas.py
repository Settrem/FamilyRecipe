
from pydantic import BaseModel
from models import RecipeStatus, FamilyMemberRole

# ----
# User Schemas
# ----

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

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    password: str | None = None


# ----
# Recipe Schemas
# ----

# The Ingridients and Recipe Steps are JSON Columns so we model them like lists here 

class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str

class RecipeStep(BaseModel):
    step_number: int
    instruction: str

class RecipeCreate(BaseModel):
    title: str
    description: str
    cooking_time: int
    portion_amount: int
    ingredients: list[Ingredient]
    recipe_instructions: list[RecipeStep]

class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    cooking_time: int | None = None
    portion_amount: int | None = None
    ingredients: list[Ingredient] | None = None
    recipe_instructions: list[RecipeStep] | None = None
    status: RecipeStatus | None = None

class RecipeRead(BaseModel):
    id: int
    author_id: int
    author_name: str

    title: str
    description: str
    cooking_time: int
    portion_amount: int

    ingredients: list[Ingredient]
    recipe_instructions: list[RecipeStep]

    status: RecipeStatus

    model_config = {
        "from_attributes": True
    }

class RecipePreview(BaseModel):
    id: int
    title: str
    cooking_time: int
    step_count: int
    ingridients: int

class RecipePreviewInFamily(BaseModel):
    id: int
    title: str
    cooking_time: int
    step_count: int
    ingredient_count: int
    recipe_creator: str

    model_config = {
        "from_attributes": True
    }

# ----
# Family Schemas
# ----

class FamilyCreate(BaseModel):
    title: str
    description: str

class FamilyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class FamilyRead(BaseModel):
    id: int
    creator: int

    title: str
    description: str

    invite_code: str

    model_config = {
        "from_attributes": True
    }

class FamilyMemberJoinRequest(BaseModel):
    family_id: int

class FamilyMemberAdd(BaseModel):
    family_id: int
    user_id: int
    family_member_role: FamilyMemberRole

class FamilyMemberUpdate(BaseModel):
    family_member_role: FamilyMemberRole

class FamilyMemberRead(BaseModel):
    user_id: int
    family_id: int
    family_member_role: FamilyMemberRole

    model_config = {
        "from_attributes": True
    }

class FamilyRecipeCreate(BaseModel):
    family_id: int
    recipe_id: int

class FamilyRecipeRead(BaseModel):
    id: int
    family_id: int
    recipe_id: int

    model_config = {
        "from_attributes": True
    }

# ----
# Favorite Recipes Schemas
# ----

class FavoriteRecipeCreate(BaseModel):
    recipe_id: int

class FavoriteRecipeRead(BaseModel):
    recipe_id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }


# ----
# Authentications schemas
# ----

class Token(BaseModel):
    access_token: str
    token_type: str
