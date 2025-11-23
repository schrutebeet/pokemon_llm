import operator

from langchain.messages import AnyMessage
from typing import TypedDict, List, Dict, Any, Optional, Annotated


class PokemonState(TypedDict):
    id: str
    name: str
    types: List[str]
    height: str
    weight: str
    abilities: Dict[str, str]
    stats: Dict[str, int]
    cries: str
    location_area_encounters: List[str]


class AppState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    pokemons: Annotated[List[PokemonState], operator.add]
    last_pokemon: Optional[PokemonState]
    user_context: Dict[str, Any]
