from typing import Union, List, Dict, Any

import requests


class DataExtractor:
    def __init__(self, source: str):
        self.source = source

    def extract_full_data(self, pokemon_name: Union[str, List] = "all") -> Dict[str, Dict]:
        # Placeholder for extraction logic
        data_output = {}
        if pokemon_name == "all":
            pass
        elif isinstance(pokemon_name, list):
            for name in pokemon_name:
                response = requests.get(f"{self.source}/{name}")
                data_output[name] = response.json()
        else:
            response = requests.get(f"{self.source}/{pokemon_name}")
            data_output[pokemon_name] = response.json()
        return data_output
    
    def extract_specific_attribute(self, pokemon_name: Union[str, List], attributes: List[str]) -> Dict[str, Dict]:
        data_output = {}
        pokemon_data = self.extract_full_data(pokemon_name)
        for pokemon_name, pokemon_data in pokemon_data.items():
            data_output[pokemon_name] = {}
            for attr in attributes:
                attr = self.__transform_attr_name(attr)
                attr_info = pokemon_data.get(attr, None)
                data_output[pokemon_name][attr] = self.__process_json_field(attr_info, attr)
        return data_output
    
    @staticmethod
    def __process_json_field(field_data: Union[str, Any], attr: str) -> Union[str, Any]:
        processed_data = None
        if attr == "id":
            processed_data = field_data
        if attr == "types":
            processed_data = field_data[0]['type']['name']
        if attr == "stats":
            for stat in field_data:
                if processed_data is None:
                    processed_data = {}
                processed_data[stat['stat']['name']] = stat['base_stat']
        if attr == "abilities":
            ability_data = {ability['ability']['name']: ability['ability']['url'] for ability in field_data}
            for ability_name, ability_url in ability_data.items():
                ability_response = requests.get(ability_url).json()
                ability_info_list = ability_response.get('effect_entries', [{}])
                ability_info_eng = [ability for ability in ability_info_list if ability["language"]["name"] == "en"]
                ability_data[ability_name] = ability_info_eng[0]["effect"] if len(ability_info_eng) else None
            processed_data = ability_data
        if attr == "cries":
            processed_data = f"The latest sound for this pokemon can be found using this link: {field_data['latest']}"
        if attr == "height":
            processed_data = DataExtractor.decimeters_to_feet_inches(field_data)
        if attr == "location_area_encounters":
            all_locations = requests.get(field_data).json()
            all_location_names = [loc['location_area']['name'].replace("-", " ").title() for loc in all_locations]
            locations = ", ".join(all_location_names) if len(all_location_names) else "This pokemon has no specific location area encounters."
            processed_data = locations
        if attr == "moves":
            move_names = [move['move']['name'].replcae("-", " ") for move in field_data]
            processed_data = ", ".join(move_names)
        return processed_data
    
    @staticmethod
    def __transform_attr_name(attr: str) -> str:
        if attr == "sound" or attr == "cry":
            return "cries"
        return attr

    def get_all_pokemon_names(self) -> Dict[str, str]:
        response = requests.get(f"{self.source}?limit=100000")
        all_pokemons = response.json()
        pokemon_names = {pokemon['name']:pokemon['url'] for pokemon in all_pokemons.get('results', [])}
        return pokemon_names

    @staticmethod
    def decimeters_to_feet_inches(decimeters: float) -> str:
        total_inches = round(decimeters * 39.3701 / 10, 0)
        feet = str(int(total_inches // 12))
        inches = str(round(total_inches % 12))
        inches = "0" + inches if len(inches) == 1 else inches
        return f"{feet}'{inches}\""