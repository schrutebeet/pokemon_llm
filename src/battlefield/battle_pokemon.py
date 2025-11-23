import numpy as np

from src.pokemon.pokemon import Pokemon
from src.pokemon.moves.moves import Moves
from src.battlefield.status import NVStatus, VStatus
from src.pokemon.moves.effectiveness import effectiveness
from config.logging import logger


class BattlePokemon(Pokemon):
    current_hp: int = None
    nvstatus: NVStatus = NVStatus.NONE
    vstatus: VStatus = VStatus.NONE
    _is_alive: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_hp = self.stats.hp

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @classmethod
    def from_pokemon_class(cls, pokemon_inst: Pokemon):
        kwargs = pokemon_inst.__dict__
        return cls(**kwargs)
    
    def change_alive_status(self) -> None:
        self._is_alive= False

    def attack(self, defender: "BattlePokemon", move: Moves) -> "BattlePokemon":
        can_move = self.is_pokemon_able_to_move()
        is_damage_inflicted = bool(np.random.choice([True, False], p=[move.accuracy/100, 1 - (move.accuracy/100)]))
        damage = self.compute_damage(defender, move) if (is_damage_inflicted and can_move) else 0
        defender = self.apply_ailment_if_move_allows(move, defender)
        defender.current_hp -= damage
        if defender.current_hp <= 0:
            defender.change_alive_status()
        return defender

    def compute_damage(self, defender: "BattlePokemon", move: Moves) -> int:
        is_attacker_burnt = self.nvstatus == NVStatus.BURNT
        criticality = (2 * self.level + 5) / (self.level + 5)
        critical_hit = bool(np.random.choice([True, False], p=[1/16, 15/16]))
        critical_mtpl = criticality * critical_hit +  1 * (not critical_hit)
        is_stab = 1.5 if move.type in defender.types else 1
        burnt_modifier = 0.5 if (is_attacker_burnt and move.damage_class == "physical") else 1
        attack_power = self.stats.attack if move.damage_class == "physical" else self.stats.special_attack
        defense_power = defender.stats.defense if move.damage_class == "physical" else defender.stats.special_defense
        random_mtpl = np.random.uniform(85, 100) / 100
        base = (((2 * self.level / 5 + 2) * move.power * attack_power / defense_power) / 50) * burnt_modifier + 2
        modifiers = critical_mtpl * is_stab * effectiveness(move.type, defender.types) * random_mtpl
        damage = int(base * modifiers)
        return damage
    
    @staticmethod
    def apply_ailment_if_move_allows(move: Moves, defender: "BattlePokemon") -> "BattlePokemon":
        if move.ailment_name != NVStatus.NONE:
            cond_prob = move.ailment_prob
            is_condition_applying = bool(np.random.choice([True, False], p=[cond_prob, 1 - cond_prob]))
            if is_condition_applying:
                defender.nvstatus = move.ailment_name
                logger.info(f"{defender.name.upper()} has been {defender.nvstatus}!")
        return defender
    
    def is_pokemon_able_to_move(self) -> bool:
        if self.nvstatus == NVStatus.PARALIZED:
            can_move = bool(np.random.choice([False, True], p=[.25, .75]))
        elif self.nvstatus == NVStatus.FROZEN or self.nvstatus == NVStatus.ASLEEP:
            can_move = False
        else:
            can_move = True
        return can_move
