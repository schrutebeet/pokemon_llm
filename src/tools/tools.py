
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
def get_pokemon_attributes(pokemon_list: list[str], **kwargs) -> dict:
    """Get specific attributes for a list of Pokemon."""
    if kwargs.get("attributes"):
        attributes = kwargs["attributes"]
    else:
        attributes = ["id", "types", "stats", "species", "abilities", "cries", "height", "weight", "base_experience", "moves"]
        
    data_extractor = DataExtractor(source="https://pokeapi.co/api/v2/pokemon")

    pokemon_info: Dict = data_extractor.extract_specific_attribute(pokemon_list, attributes)
    
    if "moves" in attributes:
        for pkmn_name, pkmn_info in pokemon_info.items():
            if "moves" in pkmn_info.keys():
                given_moves = np.random.choice(pkmn_info["moves"], size = 4, replace=False)
                final_given_moves = []
                for move in given_moves:
                    move_name = move['name'].replace("-", " ")
                    move_url = move["url"]
                    move_data = DataExtractor.extract_from_url(move_url)
                    ailment_info = {} if move_data["meta"] is None else move_data["meta"]
                    move_obj = Moves(
                        name=move_name,
                        type=move_data["type"]["name"],
                        damage_class=move_data["damage_class"]["name"],
                        accuracy=max(move_data["accuracy"] if move_data["accuracy"] is not None else 100, 20),
                        power=move_data["power"] if move_data["power"] is not None else 50,
                        pp=move_data["pp"],
                        priority=move_data["priority"],
                        stat_changes=[stat_change["change"] for stat_change in move_data.get("stat_changes", [])],
                        ailment_name=set_nvstatus_from_api(ailment_info.get("ailment", {}).get("name")),
                        ailment_prob=int(ailment_info.get("ailment_chance", 0) / 100),
                    )
                    final_given_moves.append(move_obj)
                pokemon_info[pkmn_name]["moves"] = final_given_moves
    return pokemon_info

# @tool
def return_loaded_pokemon_data(pokemon_info: dict) -> Pokemon:
    """Return a Pokemon object from loaded data."""
    output: List[Pokemon] = []
    for pkmn_name, pkmn_info in pokemon_info.items():
        pokemon_info[pkmn_name]["name"] = pkmn_name
        pokemon_info[pkmn_name]["gender"] = str(np.random.choice(["male", "female"]))
        pokemon_info[pkmn_name]["level"] = int(np.clip(1, np.random.normal(loc=50, scale=10), 100))
        pokemon_info[pkmn_name]["iv"] = IV()
        pokemon_info[pkmn_name]["ev"] = EV()
        pokemon_info[pkmn_name]["ability"] = str(np.random.choice(list(pokemon_info[pkmn_name]["abilities"].keys())))
        mod_stats = {k.replace("-", "_"): v for k,v in pokemon_info[pkmn_name]["stats"].items()}
        pokemon_info[pkmn_name]["base_stats"] = BaseStats(**mod_stats)
        pokemon_info[pkmn_name]["stats"] = Stats()

        output.append(Pokemon.model_validate(pokemon_info[pkmn_name]))
    
    return output



from src.battlefield.battle_engine import BattleEngine
from dotenv import load_dotenv

load_dotenv()

my_pokemons = ["Garbodor", "Pyukumuku"]
pokemon_attrs = get_pokemon_attributes(my_pokemons)
pokemon_attrs = return_loaded_pokemon_data(pokemon_attrs)

from langchain.chat_models import init_chat_model
llm = init_chat_model(model="openai:gpt-4o-mini")

battle = BattleEngine(*pokemon_attrs, llm=llm)
battle.start_ai_battle()
