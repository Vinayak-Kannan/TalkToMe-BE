from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

profile_budget = 0
desired_item_price = 1000

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


class Budget(BaseModel):
    budget: int

@app.get("/profile-budget",
    response_model=Budget,
    summary="Get the users budget",
    description="Get the users currently set budget",)
async def get_budget():
    return {"budget": profile_budget}
@app.post("/profile/{budget}",
    response_model=Budget,
    summary="Update the users budget",
    description="Updates the users budget to the new budget provided in the request body",)
async def update_budget(budget: int):
    profile_budget = budget
    return {"budget": profile_budget}


class Item(BaseModel):
    item_price: int
@app.get("/item",
    response_model=Item,
    summary="Get the users desired item price",
    description="Get the users set item price. This can be used in comparison to the users budget to see if the user can afford their desired item",)
async def afford_desired_item():
    return {"item_price": desired_item_price}
