from unittest.mock import patch, MagicMock
from src.main import handle_user_prompt

@patch('src.main.InferenceClient.chat.completions.create')
def test_handle_user_prompt_calls_api(mock_create):
    user_prompt = "What are the types and abilities of Pikachu?"
    mock_response = MagicMock()
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "get_pokemon_attributes"
    mock_response.choices[0].message.tool_calls = [mock_tool_call]
    mock_create.return_value = mock_response

    handle_user_prompt(user_prompt)

    mock_create.assert_called_once()
    args, kwargs = mock_create.call_args
    messages = kwargs['messages']
    assert any(msg['role'] == 'user' and msg['content'] == user_prompt for msg in messages)
    tools = kwargs['tools']
    assert any(tool['function']['name'] == 'get_pokemon_attributes' for tool in tools)