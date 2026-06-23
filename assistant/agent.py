from google import genai
from google.genai import types
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
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
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
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

# Gemini native function calling
# FAISS retrieval for catalogue grounding
# Conversation history for context retention

chat_history = []


def process_query(query):

    global chat_history

    # Save user message
    chat_history.append(
        {
            "role": "user",
            "content": query
        }
    )


    conversation = SYSTEM_PROMPT + "\n\n"

    for msg in chat_history:
        conversation += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )
    
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )


    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"""
{SYSTEM_PROMPT}

Catalogue Context:
{context}

Conversation History:
{conversation}

Current User Query:
{query}

Use the catalogue context when answering.
If an action is needed, call the appropriate tool.
""",
        config=types.GenerateContentConfig(
            tools=tools
        )
    )

    if hasattr(response, "function_calls") and response.function_calls:

        call = response.function_calls[0]

        function_name = call.name
        args = dict(call.args)
        print(f"Tool Called: {function_name}")
        print(f"Arguments: {args}")

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
            contents=f"""
{SYSTEM_PROMPT}

Catalogue Context:
{context}

User Query:
{query}

Tool Result:
{result}

Generate the final grounded response.
"""
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