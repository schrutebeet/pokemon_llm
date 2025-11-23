from dataclasses import dataclass

@dataclass
class BaseStats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0

@dataclass
class IV(BaseStats):
    pass

@dataclass
class EV(BaseStats):
    pass

@dataclass
class Stats(BaseStats):
    pass