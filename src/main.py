import os
import json
import requests
import gradio as gr
from huggingface_hub import InferenceClient

from src.config.config import Config
from src.prompts import system_prompt
from data_extractor import DataExtractor

client = InferenceClient()
config = Config()
api_url = config.get('POKEMON_API')
data_extractor = DataExtractor(source=api_url)


def handle_user_prompt(user_prompt: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt,
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
                            "pokemon_list": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of Pokemon names (lowercase, e.g., ['pikachu', 'charizard']). Extract all mentioned Pokemon from the prompt."
                            },
                            "attributes": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ['abilities', 'sound', 'cry', 'height', 'id', 'location_area_encounters', 'moves', 'species', 'stats', 'types', 'weight']
                                },
                                "description": "List of attributes requested (e.g., ['types']). Infer from the prompt what info is asked; default to ['types'] if unclear but related."
                            }
                        },
                        "required": ["pokemon_list", "attributes"]
                    }
                }
            }
        ],
        tool_choice="auto",
        )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for call in tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)

            if function_name == "get_pokemon_attributes":
                result = data_extractor.extract_specific_attribute(**arguments)

                followup = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                        response.choices[0].message,  # the assistant’s tool call message
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": function_name,
                            "content": json.dumps(result)
                        }
                    ]
                )
                return followup.choices[0].message.content
    else:
        return response.choices[0].message.content


def chat_bot(message, history = []):
    response = handle_user_prompt(message)
    return response

# Launch the UI
demo = gr.ChatInterface(
    fn=chat_bot,
    title="Pokemon LLM Chat",
    description="Ask about Pokemon types, stats, etc.!",
    examples=["What's the type of Pikachu?", "Compare stats of Charizard and Blastoise."]
)

if __name__ == "__main__":
    # demo.launch(share=True)
    print(chat_bot("what are the abilities of Iron Crown?"))