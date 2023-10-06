import json

from fastapi import FastAPI
from pydantic import BaseModel
import openai
from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware

config = dotenv_values("/Users/vinayakkannan/Desktop/Web Design/HW4/BE/Project/.env")
openai.api_key = config.get("SECRET_KEY")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

profile_budget = 500
desired_item_price = 1000

prompt = """You are a NLP interface to a website. Your job is to read the users requests to you, ask follow up 
questions as needed, and then request function calls to an API. Only use the functions you have been provided with. I will execute the function for 
you and give you the response. You will then parse the response and tell the user the result of their requests.

You can only respond with follow up questions to the user to gather information for the request body or query parameters.
You can ask clarifying questions to the user.

After you make the function call, I will give you the result. You will parse the result and respond to the user 
summarizing the result for them or make further function requests
"""

functions = [
    {
        "name": "get_budget",
        "description": "Get the users currently set budget",
        "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "integer",
                    "description": "This function does not take any parameters"
                }
            },
        }
    },
    {
        "name": "update_budget",
        "description": "Updates the users budget to the new budget provided in the request body",
        "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "integer",
                    "description": "Budget"
                }
            },
            "required": ["budget"]
        }
    },
    {
        "name": "afford_desired_item",
        "description": "Compares the users budget to the price of their desired item to see if the user can afford "
                       "their desired item",
                "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "integer",
                    "description": "This function does not take any parameters"
                }
            },
                }
    }
]

prompt_message = [{
    "role": "system",
    "content": prompt
}]


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
         description="Get the users currently set budget", )
async def get_budget():
    return {"budget": profile_budget}


@app.post("/profile/{budget}",
          response_model=Budget,
          summary="Update the users budget",
          description="Updates the users budget to the new budget provided in the request body", )
async def update_budget(budget: int):
    profile_budget = budget
    return {"budget": profile_budget}


class Item(BaseModel):
    item_price: int


@app.get("/item",
         response_model=Item,
         summary="Get the users desired item price",
         description="Get the users set item price. This can be used in comparison to the users budget to see if the user can afford their desired item", )
async def afford_desired_item():
    return {"item_price": desired_item_price}


def get_budget_function(junk):
    return profile_budget


def update_budget_function(new_budget: int):
    profile_budget = new_budget
    return "Successfully updated!"


def afford_desired_item_function(junk):
    if profile_budget >= desired_item_price:
        return "You can afford the item!"
    else:
        return "You cannot afford the item!"


available_functions = {
    "get_budget": get_budget_function,
    "update_budget": update_budget_function,
    "afford_desired_item": afford_desired_item_function
}


class Request(BaseModel):
    info: str


@app.post("/request")
async def request(info: Request):
    prompt_message.append({
        "role": "user",
        "content": info.info
    })

    prompt_message.append({
        "role": "assistant",
        "content": "Please wait a moment while I fetch the information."
    })
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt_message,
        functions=functions,
        temperature=0
    )

    response_message = response.choices[0].message
    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(function_args)

        prompt_message.append(response_message)

        prompt_message.append({
            "role": "function",
            "name": function_name,
            "content": str(function_response)
        })

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt_message,
            functions=functions,
            temperature=0
        )


    prompt_message.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })
    print(response.choices[0].message.content)
    return {"response": response.choices[0].message.content}
