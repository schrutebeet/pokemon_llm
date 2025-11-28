from pydantic import BaseModel, model_validator
from typing import List, Dict

from src.pokemon.moves.moves import Moves
from src.pokemon.types import PokemonType
from src.pokemon.stats import Stats, BaseStats, IV, EV


class Pokemon(BaseModel):
    id: int
    name: str
    gender: str
    types: List[PokemonType]
    stats: Stats
    level: int
    ability: str
    species: str
    height: float
    weight: float
    base_stats: BaseStats
    stats: Stats
    iv: IV
    ev: EV
    base_experience: int
    moves: List[Moves]

    @model_validator(mode='before')
    def compute_pokemon_stats(cls, values):
        base_stats = values["base_stats"]
        iv = values["iv"]
        ev = values["ev"]
        level = values["level"]
        for base_stat_name, base_stat_value in base_stats.__dict__.items():
            iv_stat_value = getattr(iv, base_stat_name)
            ev_stat_value = getattr(ev, base_stat_name)
            if base_stat_name == "hp":
                if base_stat_value == 1:  # For Shedinja
                    setattr(values["stats"], base_stat_name, 1)
                else:
                    value = (((2 * base_stat_value + iv_stat_value + (ev_stat_value/4)) * level) // 100) + level + 10
                    setattr(values["stats"], base_stat_name, value)
            else:
                value = (((2 * base_stat_value + iv_stat_value + (ev_stat_value/4)) * level) // 100) + 5
                setattr(values["stats"], base_stat_name, value)
        return values

    def get_move_by_name(self, move_name: str) -> Moves:
        for move in self.moves:
            if move.name.lower() == move_name.lower():
                return move
        raise ValueError(f"Move with name {move_name} not found for Pokemon {self.name}")
