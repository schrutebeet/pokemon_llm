from typing import Dict, List, Tuple
from functools import reduce
import operator

from config.logging import logger
from src.pokemon.moves.moves import Moves
from src.pokemon.types import PokemonType

# Pokémon Type Effectiveness Chart (Gen 6+ standard, up to Gen 9)
TYPE_CHART: Dict[str, Dict[str, float]] = {
    "normal":   {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire":     {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, 
                 "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water":    {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, 
                 "rock": 2, "dragon": 0.5},
    "grass":    {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, 
                 "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, 
                 "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2, "grass": 0.5, "electric": 0.5, "ground": 0, 
                 "flying": 2, "dragon": 0.5},
    "ice":      {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, 
                 "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, 
                 "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, 
                 "dark": 2, "steel": 2, "fairy": 0.5},
    "poison":   {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, 
                 "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground":   {"fire": 2, "grass": 0.5, "electric": 2, "poison": 2, 
                 "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying":   {"grass": 2, "electric": 0.5, "fighting": 2, "bug": 2, 
                 "rock": 0.5, "steel": 0.5},
    "psychic":  {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug":      {"grass": 2, "fire": 0.5, "fighting": 0.5, "poison": 0.5, 
                 "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, 
                 "steel": 0.5, "fairy": 0.5},
    "rock":     {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, 
                 "flying": 2, "bug": 2, "steel": 0.5},
    "ghost":    {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon":   {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark":     {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel":    {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, 
                 "rock": 2, "steel": 0.5, "fairy": 2},
    "fairy":    {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, 
                 "dark": 2, "steel": 0.5},
}

def effectiveness(move: Moves, defender_types: List[PokemonType]) -> float:
    """
    Calculate total effectiveness of a move against a Pokémon with 1 or 2 types.
    Returns: 0, 0.25, 0.5, 1, 2, or 4 (etc.)
    """
    move_type = move.type
    move_type = move_type.lower()
    multipliers = []
    
    for def_type in defender_types:
        def_type = def_type.lower()
        multipliers.append(TYPE_CHART.get(move_type, {}).get(def_type, 1.0))

    if len(multipliers) > 0:
        ValueError("No defender types provided.")
    
    if len(multipliers) == 1:
        return multipliers[0]
    
    if len(multipliers) == 2:
        value = reduce(operator.mul, multipliers, 1.0)
        if value > 1:
            logger.info(f"{move.name} ({move.type.value}) is very effective! ({value}x)")
        if 0 < value < 1:
            logger.info(f"{move.name} ({move.type.value}) is not very effective ({value}x).")
        if value == 0:
            logger.info(f"{move.name} ({move.type.value}) did not affect at all (0x).")
        return reduce(operator.mul, multipliers, 1.0)
    
    else:
        ValueError("Defender can only have 1 or 2 types.")


def get_effectiveness_label(multiplier: float) -> str:
    """Convert multiplier to readable text"""
    if multiplier == 0:
        return "No effect (0×)"
    elif multiplier < 1:
        if multiplier == 0.25:
            return "Not very effective (¼×)"
        elif multiplier == 0.5:
            return "Not very effective (½×)"
    elif multiplier == 1:
        return "Normally effective (1×)"
    else:
        if multiplier == 2:
            return "Super effective (2×)"
        elif multiplier == 4:
            return "Super effective (4×!!)"
    return f"{multiplier}×"

