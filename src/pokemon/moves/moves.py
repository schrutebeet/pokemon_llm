from pydantic import BaseModel
from typing import List, Dict

from src.pokemon.types import PokemonType
from src.battlefield.status import NVStatus


class Moves(BaseModel):
    name: str
    type: PokemonType
    damage_class: str
    accuracy: int
    power: int
    pp: int
    priority: int
    stat_changes: List[int]
    ailment_name: NVStatus
    ailment_prob: int
