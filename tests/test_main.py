import json
import unittest
from unittest.mock import patch, MagicMock

from src.prompts import system_prompt
from src.main import handle_user_prompt

@patch('src.main.client')
def test_no_tool_call(mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.content = "I am fine, thank you!"
    mock_client.chat.completions.create.return_value = mock_response

    user_prompt = "Hello, how are you?"
    result = handle_user_prompt(user_prompt)

    assert result == "I am fine, thank you!"
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args.kwargs
    assert call_args['model'] == "openai/gpt-oss-120b"
    assert {"role": "system", "content": system_prompt} in call_args['messages']
    assert {"role": "user", "content": user_prompt} in call_args['messages']

@patch('src.main.data_extractor')
@patch('src.main.client')
def test_with_tool_call(mock_client, mock_data_extractor):
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "get_pokemon_attributes"
    mock_tool_call.function.arguments = json.dumps({
        "pokemon_list": ["pikachu"],
        "attributes": ["types"]
    })
    mock_tool_call.id = "tool_call_id_123"

    mock_initial_response = MagicMock()
    mock_initial_response.choices = [MagicMock()]
    mock_initial_response.choices[0].message.tool_calls = [mock_tool_call]
    mock_initial_response.choices[0].message.content = None

    mock_followup_response = MagicMock()
    mock_followup_response.choices = [MagicMock()]
    mock_followup_response.choices[0].message.content = "Final response with Pokemon data"

    # Side effect is used to return different responses on consecutive calls
    # So, on the first client.chat.completions.create call, it returns mock_initial_response
    # and on the second call, it returns mock_followup_response
    mock_client.chat.completions.create.side_effect = [mock_initial_response, mock_followup_response]

    mock_data_extractor.extract_specific_attribute.return_value = {"pikachu": {"types": ["electric"]}}

    user_prompt = "What's the type of Pikachu?"
    result = handle_user_prompt(user_prompt)

    assert result == "Final response with Pokemon data"
    assert mock_client.chat.completions.create.call_count == 2

    first_call_args = mock_client.chat.completions.create.call_args_list[0].kwargs
    assert first_call_args['model'] == "openai/gpt-oss-120b"
    assert {"role": "user", "content": user_prompt} in first_call_args['messages']

    mock_data_extractor.extract_specific_attribute.assert_called_once_with(
        pokemon_list=["pikachu"],
        attributes=["types"]
    )

    second_call_args = mock_client.chat.completions.create.call_args_list[1].kwargs
    assert second_call_args['model'], "openai/gpt-oss-120b"
    messages = second_call_args['messages']
    assert len(messages) == 4
    assert {"role": "tool", "tool_call_id": "tool_call_id_123", "name": "get_pokemon_attributes", "content": json.dumps({"pikachu": {"types": ["electric"]}})} in messages
