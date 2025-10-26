import unittest
from unittest.mock import patch, MagicMock
from src.data_extractor import DataExtractor

def test_data_extractor_initialization():
    source_url = "https://pokeapi.co/api/v2/pokemon"
    extractor = DataExtractor(source=source_url)
    assert extractor.source == source_url

@patch('src.data_extractor.requests.get')
def test_extract_full_data_all(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "This is some Pikachu data"}
    mock_get.return_value = mock_response

    extractor = DataExtractor(source="https://pokeapi.co/api/v2/pokemon")
    data = extractor.extract_full_data(pokemon_name="pikachu")
    assert data == {"pikachu": {"name": "This is some Pikachu data"}}

def test_convert_decimeters_to_feet_inches():
    height_decimeters = 18.034
    expected_output = "5'11\""
    output = DataExtractor.convert_decimeters_to_feet_inches(height_decimeters)
    assert output == expected_output

@patch('src.data_extractor.requests.get')
def test_get_all_pokemon_names(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "count": 1328,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon/1/"
            },
            {
                "name": "ivysaur",
                "url": "https://pokeapi.co/api/v2/pokemon/2/"
            }
        ]
    }
    mock_get.return_value = mock_response
    extractor = DataExtractor(source="https://pokeapi.co/api/v2/pokemon")
    names = extractor.get_all_pokemon_names()
    assert isinstance(names, dict)
    assert names == {'bulbasaur': 'https://pokeapi.co/api/v2/pokemon/1/', 'ivysaur': 'https://pokeapi.co/api/v2/pokemon/2/'}

