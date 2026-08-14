from fastapi import FastAPI

from database import Base, engine

from routers import (
    authentication,
    users,
    recipes,
    family_crud,
)


Base.metadata.create_all(bind=engine)

app = FastAPI()


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