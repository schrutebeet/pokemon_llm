
from typing import List, Any

import numpy as np
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

from config.logging import logger
from src.pokemon.pokemon import Pokemon
from src.pokemon.moves.moves import Moves
from src.battlefield.status import NVStatus
from src.battlefield.battle_pokemon import BattlePokemon
from src.battlefield.prompts import POKEMON_TRAINER


class BattleEngine:
    def __init__(self, user_pokemon: Pokemon | BattlePokemon,
                 foe_pokemon: Pokemon | BattlePokemon,
                 llm: ChatOpenAI | Any) -> None:
        self.user_pokemon = BattlePokemon.from_pokemon_class(user_pokemon) if isinstance(user_pokemon, Pokemon) else user_pokemon
        self.foe_pokemon = BattlePokemon.from_pokemon_class(foe_pokemon) if isinstance(foe_pokemon, Pokemon) else foe_pokemon
        if self.user_pokemon.name == self.foe_pokemon.name:
            self.user_pokemon.name += " 1"
            self.foe_pokemon.name += " 2"
        self.llm =llm

    def start_battle(self):
        # TODO
        logger.info("Battle has started!")
        logger.info(f"Battle is between {self.user_pokemon.name.upper()} and {self.foe_pokemon.name}")

        
    def start_ai_battle(self):
        logger.info("Battle has started!")
        logger.info(f"Battle is between {self.user_pokemon.name.upper()} and {self.foe_pokemon.name.upper()}")
        logger.info(
            f"{self.user_pokemon.name.upper()} is at level {self.user_pokemon.level} and starts with {self.user_pokemon.stats.hp} HP"
        )
        logger.info(
            f"and {self.foe_pokemon.name.upper()} is at level {self.foe_pokemon.level} and starts with {self.foe_pokemon.stats.hp} HP"
        )
        logger.info(
            f"{self.user_pokemon.name.upper()} can use {", ".join([move.name for move in self.user_pokemon.moves])} as moves"
        )
        logger.info(
            f"{self.foe_pokemon.name.upper()} can use {", ".join([move.name for move in self.foe_pokemon.moves])} as moves"
        )
        who_starts = self.user_pokemon if self.user_pokemon.stats.speed > self.foe_pokemon.stats.speed else self.foe_pokemon
        who_follows =  self.user_pokemon if self.user_pokemon.stats.speed <= self.foe_pokemon.stats.speed else self.foe_pokemon
        logger.info(f"{who_starts.name.upper()} moves first")
        round_count = 1
        while True:
            logger.info(f"Moving to round #{round_count}")
            # First pokemon runs its turn
            who_starts, who_follows = self.run_pokemon_turn(who_starts, who_follows)
            if not who_follows.is_alive:
                logger.info(f"{who_follows.name.upper()} has fainted!")
                break
            # Second pokemon runs its turn
            who_follows, who_starts = self.run_pokemon_turn(who_follows, who_starts)
            if not who_starts.is_alive:
                logger.info(f"{who_starts.name.upper()} has fainted!")
                break
            # Execute condition consequences
            who_starts, who_follows = self.execute_status_consequences(who_starts, who_follows)
            if not who_starts.is_alive:
                logger.info(f"{who_starts.name.upper()} has fainted!")
                break
            who_starts, who_follows = self.update_status_condition(who_starts, who_follows)
            who_starts, who_follows = self.update_who_starts_first(who_starts, who_follows)
            logger.info(
                f"End of round - {self.user_pokemon.name.upper()} has {self.user_pokemon.current_hp} HP left "
                f"and {self.foe_pokemon.name.upper()} has {self.foe_pokemon.current_hp} HP left"
            )
            round_count += 1

        winner = who_starts if who_starts.is_alive else who_follows
        logger.info(f"{winner.name.upper()} wins!")
        self.end_battle()
    
    @staticmethod
    def update_status_condition(*args: BattlePokemon) -> List[BattlePokemon]:
        updated_pokemon_list = []
        for pkmn in args:
            if pkmn.nvstatus != NVStatus.NONE:
                reset_conditions = bool(np.random.choice([True, False], p=[.25, .75]))
                pkmn.nvstatus = NVStatus.NONE if reset_conditions else pkmn.nvstatus
                if reset_conditions:
                    logger.info(f"{pkmn.name.upper()} is no longer {pkmn.nvstatus.value}!")
            if pkmn.nvstatus == NVStatus.PARALIZED:
                pkmn.stats.speed *= 0.75
            updated_pokemon_list.append(pkmn)
        return updated_pokemon_list

    @staticmethod
    def get_move_by_name(moves: List[Moves], name: str) -> Moves:
        name = name.strip().lower()
        move = next((move for move in moves if move.name == name), None)
        if move is None:
            ValueError("Move returned by LLM does not match with any of the pokemon's moves")
        return move
    
    def run_pokemon_turn(self, attacker: BattlePokemon, defender: BattlePokemon) -> List[BattlePokemon]:
        updated_trainer_info = POKEMON_TRAINER.format(
            user_pokemon = attacker.name,
            foe_pokemon = defender.name,
            user_stats = attacker.stats,
            foe_stats = defender.stats,
            user_nvstatus = attacker.nvstatus.value,
            foe_nvstatus = defender.nvstatus.value,
            moves = attacker.moves
        )
        move_pick = self.bind_model_response_to_move_name_and_explanation(updated_trainer_info, self.llm)
        logger.info(f"{attacker.name.upper()} has chosen to attack with '{move_pick.move}'")
        logger.debug(f"Reason: '{move_pick.explanation}'")
        move = self.get_move_by_name(attacker.moves, move_pick.move)
        defender = attacker.attack(defender, move)
        return attacker, defender

    @staticmethod
    def execute_status_consequences(*args: BattlePokemon) -> List[BattlePokemon]:
        updated_pokemon_list = []
        for pkmn in args:
            if pkmn.nvstatus == NVStatus.BURNT or pkmn.nvstatus == NVStatus.POISONED:
                pkmn.current_hp -= int(pkmn.stats.hp / 8)
                logger.info(f"{pkmn.name.upper()} has lost {int(pkmn.stats.hp / 8)} HP due to being {pkmn.nvstatus.value}!")
                if pkmn.current_hp <= 0:
                    pkmn.change_alive_status()

            updated_pokemon_list.append(pkmn)
        return updated_pokemon_list

    @staticmethod
    def update_who_starts_first(who_starts: BattlePokemon, who_follows: BattlePokemon) -> List[BattlePokemon]:
        if who_starts.stats.speed < who_follows.stats.speed:
            now_second_place = who_starts
            who_starts, who_follows = who_follows, now_second_place
            logger.info(f"{now_second_place.name.upper()} now moves second! {who_follows.name.upper()} moves first.")
        return who_starts, who_follows
    
    @staticmethod
    def bind_model_response_to_move_name_and_explanation(triner_message: str, llm: ChatOpenAI) -> Any:

        class MoveDecision(BaseModel):
            move: str = Field(description="The exact name of the move to use")
            explanation: str = Field(description="Clear tactical reason for choosing this move")

        parser = PydanticOutputParser(pydantic_object=MoveDecision)
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", triner_message),
                ("human", """You MUST respond with valid JSON that matches this schema:
                            {format_instructions}

                            Your response must contain ONLY the JSON object, nothing else.
                            """.strip()),
            ]
        )
        chain = prompt | llm | parser
        decision = chain.invoke({"format_instructions": parser.get_format_instructions()})
        logger.debug("LLM request ran successfully.")
        
        return decision
        

    def end_battle(self) -> None:
        logger.info(f"Battle has concluded")
