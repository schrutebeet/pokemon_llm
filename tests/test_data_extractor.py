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
    data_str = extractor.extract_full_data(pokemon_name="pikachu")
    data_list = extractor.extract_full_data(pokemon_name=["pikachu"])
    assert data_str == {"pikachu": {"name": "This is some Pikachu data"}}
    assert data_str == data_list

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

@patch('src.data_extractor.DataExtractor.extract_full_data')
def test_extract_specific_attribute(mock_extract_full_data):
    mock_extract_full_data.return_value = {
        "pikachu": {
            "types": [
                {
                    "slot": 1,
                    "type": {
                        "name": "electric",
                        "url": "https://pokeapi.co/api/v2/type/13/"
                    }
                }
            ],
            "weight": 60
        }
    }
    extractor = DataExtractor(source="https://pokeapi.co/api/v2/pokemon")
    attributes = extractor.extract_specific_attribute(pokemon_list=["pikachu"], attributes=["types", "weight"])
    assert attributes == {'pikachu': {'types': 'electric', 'weight': '13.23 lbs (or 6.0 kg)'}}

def test__process_id_json_field():
    output = DataExtractor._process_json_field(25, "id")
    assert output == 25

def test__process_stats_json_field():
    stats_data =[{"base_stat": 35, "stat": {"name": "hp"}}, {"base_stat": 55, "stat": {"name": "attack"}}, {"base_stat": 40, "stat": {"name": "defense"}}]
    output = DataExtractor._process_json_field(stats_data, "stats")
    assert output == {'hp': 35, 'attack': 55, 'defense': 40}

@patch('src.data_extractor.requests.get')
def test__process_abilities_json_field(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"effect_entries":[{"effect":"Ability in German.","language":{"name":"de"}},{"effect":"Ability in English","language":{"name":"en"}}]}
    mock_get.return_value = mock_response
    abilities_data = [{"ability": {"name": "static", "url": "/url/static"}}, {"ability": {"name": "lightning-rod", "url": "/url/lightning-rod"}}]
    output = DataExtractor._process_json_field(abilities_data, "abilities")
    assert output == {'static': 'Ability in English', 'lightning-rod': 'Ability in English'}

@patch('src.data_extractor.requests.get')
def test__location_area_encounters_json_field(mock_get):
    response_mock = MagicMock()
    response_mock.json.return_value = [{'location_area': {'name': 'kanto-route-1'}}, {'location_area': {'name': 'trophy-garden-area'}}]
    mock_get.return_value = response_mock
    location_area_encounters_data = {"location_area_encounters": "https://pokeapi.co/api/v2/pokemon/1/encounters"}
    output = DataExtractor._process_json_field(location_area_encounters_data, "location_area_encounters")
    assert output == "Kanto Route 1, Trophy Garden Area"

@patch('src.data_extractor.requests.get')
def test__process_species_json_field(mock_get):
    response_mock = MagicMock()
    response_mock.json.return_value = {"genera": [{"genus": "Pokémon Ratón", "language": {"name": "es"}}, {"genus": "Mouse Pokémon", "language": {"name": "en"}}]}
    mock_get.return_value = response_mock
    species_data = {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon-species/25/"}
    output = DataExtractor._process_json_field(species_data, "species")
    assert output == "Mouse"

def test__process_moves_json_field():
    moves_data = [{"move": {"name": "thunder-shock"}}, {"move": {"name": "quick-attack"}}]
    output = DataExtractor._process_json_field(moves_data, "moves")
    assert output == "thunder shock, quick attack"

def test__process_height_json_field():
    height_data = 18.034
    output = DataExtractor._process_json_field(height_data, "height")
    assert output == "5'11\""
