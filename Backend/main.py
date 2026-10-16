from fastapi import FastAPI

from database import Base, engine

#To add a new route add its file name in the imoport here and the include the route in the app as seen below
from routers import (
    authentication,
    users,
    recipes,
    family_crud,
    family_join,
    family_recipes,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

#Here we include the routes inside the app
app.include_router(
    authentication.router
)

app.include_router(
    users.router
)

app.include_router(
    recipes.router
)

app.include_router(
    family_crud.router
)

app.include_router(
    family_join.router
)

app.include_router(
    family_recipes.router
)