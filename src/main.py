import os
import json
import requests
from huggingface_hub import InferenceClient

from src.config.config import Config
from src.data_extraction.data_extractor import DataExtractor

client = InferenceClient()
config = Config()
api_url = config.get('POKEMON_API')
data_extractor = DataExtractor(source=api_url)


# System prompt to guide the LLM

USER_PROMPT = "what are the moves pikachu can learn?"

system_prompt = """
You are a Pokemon expert assistant. When a user asks about Pokemon attributes like type, stats, etc., use the get_pokemon_attributes function to fetch data.
Do not answer directly; always call the function if it matches.
Normalize Pokemon names to lowercase official spellings (e.g., 'Pikachu' -> 'pikachu').
If multiple attributes are asked (e.g., types and weaknesses), include them in 'attribute'.
If no specific attribute, infer the closest (e.g., 'what is Pikachu?' -> ['types', 'stats']).
When usin the function, ensure 'pokemon_name' is a **list** of names, e.g., ["pikachu"]; and 'attribute' is a **list** of requested attributes, e.g., ["types"].
If user asks for height, state both measures in feet and meters.
"""

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": USER_PROMPT,
        }
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_pokemon_attributes",
                "description": "Fetch specific attributes for Pokemon.",
                "parameters": { 
                    "type": "object",
                    "properties": {
                        "pokemon_name": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of Pokemon names (lowercase, e.g., ['pikachu', 'charizard']). Extract all mentioned Pokemon from the prompt."
                        },
                        "attributes": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ['abilities', 'sound', 'cry', 'height', 'id', 'location_area_encounters', 'moves', 'name', 'order', 'past_abilities', 'past_types', 'species', 'sprites', 'stats', 'types', 'weight']
                            },
                            "description": "List of attributes requested (e.g., ['types']). Infer from the prompt what info is asked; default to ['types'] if unclear but related."
                        }
                    },
                    "required": ["pokemon_name", "attributes"]
                }
            }
        }
    ],
    tool_choice="auto",  # Let LLM decide if/when to call
    )

tool_calls = response.choices[0].message.tool_calls
if tool_calls:
    for call in tool_calls:
        function_name = call.function.name
        arguments = json.loads(call.function.arguments)

        # 3️⃣ Run your actual function in Python
        if function_name == "get_pokemon_attributes":
            result = data_extractor.extract_specific_attribute(**arguments)

            # 4️⃣ Send function result back to the model to get a human-style answer
            followup = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": USER_PROMPT},
                    response.choices[0].message,  # the assistant’s tool call message
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    }
                ]
            )
            print(followup.choices[0].message.content)
else:
    # No tool call — model answered directly
    print(response.choices[0].message.content)
