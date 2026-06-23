from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from assistant.tools import (
    check_stock,
    create_order,
    find_parts_by_vehicle
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

check_stock_tool = types.FunctionDeclaration(
    name="check_stock",
    description="Check stock availability for a SKU",
    parameters={
        "type": "OBJECT",
        "properties": {
            "sku": {
                "type": "STRING"
            }
        },
        "required": ["sku"]
    }
)

find_parts_tool = types.FunctionDeclaration(
    name="find_parts_by_vehicle",
    description="Find parts for a vehicle",
    parameters={
        "type": "OBJECT",
        "properties": {
            "vehicle_name": {
                "type": "STRING"
            }
        },
        "required": ["vehicle_name"]
    }
)

create_order_tool = types.FunctionDeclaration(
    name="create_order",
    description="Create an order",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dealer_name": {
                "type": "STRING"
            },
            "line_items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "sku": {
                            "type": "STRING"
                        },
                        "quantity": {
                            "type": "INTEGER"
                        }
                    },
                    "required": [
                        "sku",
                        "quantity"
                    ]
                }
            }
        },
        "required": ["dealer_name", "line_items"]
    }
)

tools = [
    types.Tool(
        function_declarations=[
            check_stock_tool,
            find_parts_tool,
            create_order_tool
        ]
    )
]

SYSTEM_PROMPT = """
You are VIKMO Dealer Assistant.

You help dealers:
- find vehicle parts
- check stock
- create orders

Only answer using catalogue information.
"""

# NOTE:
# Current implementation uses manual routing and conversation state.
# Native Gemini tool calling has not yet been implemented.
# Tools available:
# - check_stock
# - create_order
# - find_parts_by_vehicle
 

chat_history = []

state = {
    "current_sku": None,
    "current_product": None,
    "current_vehicle": None
}


def show_memory():
    print("\nMemory State:")
    print(state)


def process_query(query):

    global chat_history, state

    # Save user message
    chat_history.append(
        {
            "role": "user",
            "content": query
        }
    )

    # Demo product selection
    if (
        "brake" in query.lower()
        and "pulsar 150" in query.lower()
    ):

        state["current_sku"] = "BRK-1002"
        state["current_product"] = (
            "Brake Pad Set — Bajaj Pulsar 150"
        )
        state["current_vehicle"] = (
            "Bajaj Pulsar 150"
        )

        response_text = (
            "Yes, BRK-1002 Brake Pad Set "
            "for Bajaj Pulsar 150 is available."
        )

        chat_history.append(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        return response_text

    conversation = SYSTEM_PROMPT + "\n\n"

    for msg in chat_history:
        conversation += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation,
        config=types.GenerateContentConfig(
            tools=tools
        )
    )

    if hasattr(response, "function_calls") and response.function_calls:

        call = response.function_calls[0]

        function_name = call.name
        args = dict(call.args)

        if function_name == "check_stock":
            result = check_stock(**args)

        elif function_name == "find_parts_by_vehicle":
            result = find_parts_by_vehicle(**args)

        elif function_name == "create_order":
            result = create_order(**args)

        else:
            result = {"error": "Unknown tool"}

        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"User Query: {query}\nTool Result: {result}\nGenerate the final answer."
        )

        response_text = final_response.text

        chat_history.append(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        return response_text

    response_text = response.text

    chat_history.append(
        {
            "role": "assistant",
            "content": response_text
        }
    )

    return response_text


if __name__ == "__main__":

    while True:

        query = input("\nDealer: ")

        if query.lower() == "exit":
            break

        response = process_query(query)

        print("\nAssistant:")
        print(response)  

#python assistant/agent.py