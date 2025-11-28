
from typing import Dict, List

import numpy as np
from langchain.tools import tool

from src.data_extractor import DataExtractor
from src.pokemon.pokemon import Pokemon
from src.pokemon.stats import IV
from src.pokemon.stats import EV
from src.pokemon.stats import BaseStats, Stats
from src.pokemon.moves.moves import Moves
from src.battlefield.status import set_nvstatus_from_api


# @tool
def get_pokemon_attributes(pokemon_list: List[str], **kwargs) -> List:
    """Get specific attributes for a list of Pokemon."""
    if kwargs.get("attributes"):
        attributes = kwargs["attributes"]
    else:
        attributes = ["id", "types", "stats", "species", "abilities", "cries", "height", "weight", "base_experience", "moves"]

    data_extractor = DataExtractor(source="https://pokeapi.co/api/v2/pokemon")

    pokemon_list: List = data_extractor.extract_specific_attribute(pokemon_list, attributes)
    final_list = []
    if "moves" in attributes:
        for pokemon in pokemon_list:
            if "moves" in pokemon.keys():
                given_moves = np.random.choice(pokemon["moves"], size = min(len(pokemon["moves"]), 4), replace=False)
                final_given_moves = []
                for move in given_moves:
                    move_name = move['name'].replace("-", " ")
                    move_url = move["url"]
                    move_data = DataExtractor.extract_from_url(move_url)
                    ailment_info = {} if move_data["meta"] is None else move_data["meta"]
                    move_obj = Moves(
                        name=move_name,
                        description=move_data["flavor_text_entries"][0]["flavor_text"],
                        type=move_data["type"]["name"],
                        damage_class=move_data["damage_class"]["name"],
                        accuracy=max(move_data["accuracy"] if move_data["accuracy"] is not None else 100, 20),
                        power=move_data["power"] if move_data["power"] is not None else 50,
                        pp=move_data["pp"],
                        priority=move_data["priority"],
                        stat_changes=[stat_change["change"] for stat_change in move_data.get("stat_changes", [])],
                        ailment_name=set_nvstatus_from_api(ailment_info.get("ailment", {}).get("name")),
                        ailment_prob=ailment_info.get("ailment_chance", 0) / 100,
                    )
                    final_given_moves.append(move_obj)
            pokemon["moves"] = final_given_moves
            final_list.append(pokemon)
    return final_list

# @tool
def return_loaded_pokemon_data(pokemon_info: List) -> List[Pokemon]:
    """Return a Pokemon object from loaded data."""
    output: List[Pokemon] = []
    for pkmn_info in pokemon_info:
        pkmn_info["gender"] = str(np.random.choice(["male", "female"]))
        pkmn_info["level"] = int(np.clip(1, np.random.normal(loc=50, scale=10), 100))
        pkmn_info["iv"] = IV()
        pkmn_info["ev"] = EV()
        pkmn_info["ability"] = str(np.random.choice(list(pkmn_info["abilities"].keys())))
        mod_stats = {k.replace("-", "_"): v for k,v in pkmn_info["stats"].items()}
        pkmn_info["base_stats"] = BaseStats(**mod_stats)
        pkmn_info["stats"] = Stats()

        output.append(Pokemon.model_validate(pkmn_info))
    
    return output



from src.battlefield.battle_engine import BattleEngine
from dotenv import load_dotenv

load_dotenv()

my_pokemons = ["Charizard", "Charizard"]
pokemon_attrs = get_pokemon_attributes(my_pokemons)
pokemon_attrs = return_loaded_pokemon_data(pokemon_attrs)

from langchain.chat_models import init_chat_model
llm = init_chat_model(model="openai:gpt-4o-mini")

battle = BattleEngine(*pokemon_attrs, llm=llm)
battle.start_ai_battle()
