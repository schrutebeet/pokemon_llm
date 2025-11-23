import copy
from typing import Union, List, Dict, Any, Annotated

import requests

GAME_TO_REPLICATE = "emerald"


class DataExtractor:
    def __init__(self, source: str):
        self.source = source

    def extract_full_data(self, pokemon_name: Union[str, List] = "all") -> List[str]:
        # Placeholder for extraction logic
        data_output = []
        if pokemon_name == "all":
            pass
        elif isinstance(pokemon_name, list):
            for name in pokemon_name:
                response = requests.get(f"{self.source}/{name}")
                pokemon_info = response.json()
                pokemon_info["name"] = name
                data_output.append(pokemon_info)
        else:
            response = requests.get(f"{self.source}/{pokemon_name}")
            pokemon_info = response.json()
            pokemon_info["name"] = name
            data_output.append(pokemon_info)
        return data_output
    
    def extract_specific_attribute(self, pokemon_list: Union[str, List], attributes: List[str]) -> List[str]:
        output = []
        pokemon_data = self.extract_full_data(pokemon_list)
        for pkmn_info in pokemon_data:
            for attr in attributes:
                attr = self.__transform_attr_name(attr)
                attr_info = pkmn_info.get(attr, None)
                pkmn_info[attr] = self._process_json_field(attr_info, attr)
            output.append(pkmn_info)
        return output
    
    @staticmethod
    def _process_json_field(field_data: Union[str, Any], attr: str) -> Union[str, Any]:
        processed_data = None
        if attr == "id":
            processed_data = field_data
        if attr == "types":
            processed_data = [pkmn_type['type']['name'] for pkmn_type in field_data]
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
            # processed_data = DataExtractor.convert_decimeters_to_feet_inches(field_data)
            processed_data = round(field_data / 10, 2)
        if attr == "location_area_encounters":
            all_locations = requests.get(field_data).json()
            all_location_names = [loc['location_area']['name'].replace("-", " ").title() for loc in all_locations]
            locations = ", ".join(all_location_names) if len(all_location_names) else "This pokemon has no specific location area encounters."
            processed_data = locations
        if attr == "moves":
            processed_data = []
            for move in field_data:
                is_in_game = any([game["version_group"]["name"] == GAME_TO_REPLICATE for game in move["version_group_details"]])
                if is_in_game:
                    processed_data.append(move['move'])
        if attr == "species":
            species_response = requests.get(field_data['url']).json()
            species_eng = [species["genus"] for species in species_response.get('genera', [{}]) if species["language"]["name"] == "en"]
            species_eng_name = species_eng[0] if len(species_eng) else "No species found"
            processed_data = species_eng_name.replace(" Pokémon", "")
        if attr == "weight":
            # processed_data = DataExtractor.convert_hectograms_to_pounds(field_data)
            # processed_data += f" (or {DataExtractor.convert_hectograms_to_kilograms(field_data)})"
            processed_data = round(field_data / 10, 2)
        if attr == "base_experience":
            # processed_data = DataExtractor.convert_hectograms_to_pounds(field_data)
            # processed_data += f" (or {DataExtractor.convert_hectograms_to_kilograms(field_data)})"
            processed_data = field_data
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
    def convert_decimeters_to_feet_inches(decimeters: float) -> str:
        total_inches = round(decimeters * 39.3701 / 10, 0)
        feet = str(int(total_inches // 12))
        inches = str(round(total_inches % 12))
        inches = "0" + inches if len(inches) == 1 else inches
        return f"{feet}'{inches}\""
    
    @staticmethod
    def convert_hectograms_to_pounds(hectograms: float) -> str:
        pounds = round(hectograms * 0.220462, 2)
        return f"{pounds} lbs"
    
    @staticmethod
    def convert_hectograms_to_kilograms(hectograms: float) -> str:
        kilograms = round(hectograms / 10, 2)
        return f"{kilograms} kg"

    @staticmethod
    def extract_from_url(url: str) -> Dict[str, Any]:
        response = requests.get(url)
        return response.json()
