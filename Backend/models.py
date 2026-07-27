from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Enum, JSON, UniqueConstraint
from sqlalchemy.sql import func
import enum
from database import Base

# -------------------------
# ENUMS
# -------------------------

# -- RecipeStatus -- 
# This is datatype that lets the application know what status a recipe is in

class RecipeStatus(enum.Enum):
    Archived = "Archived"
    Released = "Released"
    Not_Finished = "Not_Finished"

# -- RecipeStatus -- 
# This is datatype that sets the role of a family member and how much authority they have in the family

class FamilyMemberRole(enum.Enum):
    Administrator = "Administrator"
    Editor = "Editor"
    Visitor = "Visitor"

# -------------------------
# Database Schemas
# -------------------------

# -- User -- 
# This is the schema for our users

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(256), unique=True, index=True)
    password_hash = Column(String)
    disabled = Column(Boolean, index=True, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# -- Recipe -- 
# This is the schema for the Recipes which uses JSON format to store recipes ingridients,
# the iingriedients are not Normalized as it would result in long computation time to
# query all ingredients and we would also have repeating rows. 

class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    title = Column(String(50))
    description = Column(Text)
    cooking_time = Column(Integer)
    portion_amount = Column(Integer)

    ingredients = Column(JSON)
    recipe_instructions = Column(JSON)

    status = Column(Enum(RecipeStatus))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# -- Family -- 
# This is the schema for the different families which is were users can share their recipies in

class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    creator = Column(Integer, ForeignKey("user.id"), nullable=False)

    title = Column(String(50))
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# -- Family Recipe-- 
# This is the schema for when a user wants to allow a family to see one of their specific recipes

class FamilyRecipe(Base):
    __tablename__ = "family_recipe"

    __table_args__ = (
        UniqueConstraint(
            "family_id",
            "recipe_id",
            name="unique_family_recipe"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    family_id = Column(Integer, ForeignKey("family.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# -- Family Member-- 
# This is the schema for telling which families users are in and their status/Role in that family

class FamilyMember(Base):
    __tablename__ = "faimly_member"    

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "family_id",
            name="unique_family_member"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    family_id = Column(Integer, ForeignKey("family.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    family_member_role = Column(Enum(FamilyMemberRole))

    joined_at = Column(DateTime(timezone=True), server_default=func.now())

# -- Family Member-- 
# This is the schema for allowing which famelies can see your recipies and not

class FavoriteRecipe(Base):
    __tablename__ = "favorite_recipe"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "recipe_id",
            name="unique_favorite_recipe"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
        
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    saved_at = Column(DateTime(timezone=True), server_default=func.now())

# -- Family Member-- 
# This is the schema for users to request to join a family

class RequestToJoinFamily(Base):
    __tablename__ = "request_to_join_family"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    family_id = Column(Integer, ForeignKey("family.id"), primary_key=True)
    requested_by = Column(Integer, ForeignKey("user.id"), primary_key=True)

    requested_at = Column(DateTime(timezone=True), server_default=func.now())