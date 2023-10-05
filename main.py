from fastapi import FastAPI
from pydantic import BaseModel
import openai
from dotenv import dotenv_values

config = dotenv_values("/Users/vinayakkannan/Desktop/Web Design/HW4/BE/Project/.env")
openai.api_key = config.get("SECRET_KEY")

app = FastAPI()

profile_budget = 0
desired_item_price = 1000

prompt = """You are a NLP interface to a website. Your job is to read the users requests to you, ask follow up 
questions as needed, and then create Javascript commands to make request to an API. I will execute the javascript for 
you and give you the response. You will then parse the response and tell the user the result of their requests.

You can only respond with follow up questions to the user to gather information for the request body or query parameters.
You can ask clarifying questions to the user.
You can only respond with either the relevant Javascript code to make the request.
I will give you the result of the request and then you will parse the result and respond to the user.

The API schema path, as defined by OpenAPI, is below:
  "paths": {
    "/": {
      "get": {
        "summary": "Root",
        "operationId": "root__get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/hello/{name}": {
      "get": {
        "summary": "Say Hello",
        "operationId": "say_hello_hello__name__get",
        "parameters": [
          {
            "name": "name",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Name"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/profile-budget": {
      "get": {
        "summary": "Get the users budget",
        "description": "Get the users currently set budget",
        "operationId": "get_budget_profile_budget_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Budget"
                }
              }
            }
          }
        }
      }
    },
    "/profile/{budget}": {
      "post": {
        "summary": "Update the users budget",
        "description": "Updates the users budget to the new budget provided in the request body",
        "operationId": "update_budget_profile__budget__post",
        "parameters": [
          {
            "name": "budget",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "Budget"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Budget"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/item": {
      "get": {
        "summary": "Get the users desired item price",
        "description": "Get the users set item price. This can be used in comparison to the users budget to see if the user can afford their desired item",
        "operationId": "afford_desired_item_item_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Item"
                }
              }
            }
          }
        }
      }
    }
  }
"""

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


@app.post("/request}")
async def request(info: str):
    prompt_message.append({
        "role": "user",
        "content": info
    })
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt_message,
        temperature=0
    )
    prompt_message.append({
        "role": "system",
        "content": response.choices[0].text
    })
    return {"response": response.choices[0].text}
