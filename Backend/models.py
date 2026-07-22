from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    disabled = Column(Boolean, index=True, default=False)
    hashed_password = Column(String, index=True)

class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String, index=True)
    creator_id = Column(Integer, ForeignKey("user.id"))