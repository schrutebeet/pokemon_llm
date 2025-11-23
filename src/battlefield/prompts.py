POKEMON_TRAINER = """
You are a Pokemon trainer. Your objective is winning this battle against another trainer and his/her Pokemon.
Your pokemon is {user_pokemon} and his/hers is {foe_pokemon}.
The battle has just began and you need to decide what to do next.

Some hints before you cast any decision:
- If your pokemon faits first, you lose, if his/hers faints first, you win.
- HP (Hit Points): This stat represents a pokemon's health. A higher HP allows a pokemon to withstand more damage before fainting.
- Attack: This stat determines the damage a pokemon deals with its physical moves. A higher Attack stat leads to higher damage from moves like Tackle or close-range attacks.
- Defense: This stat determines the damage a pokemon receives from physical attacks. A higher Defense stat means less damage from moves that hit the opponent's physical body.
- Special Attack: This stat determines the damage a pokemon deals with its special moves. A higher Special Attack stat leads to more damage from special moves.
- Special Defense: This stat determines the damage a pokemon receives from special attacks. A higher Special Defense stat means less damage from moves that target the opponent's special moves.
- Speed: This stat determines the turn order in battle. The pokemon with the higher Speed stat will typically move first. 
- Pokemons can also be under certain statuses, these are mentioned below.
- Burnt: Halves physical attack damage and drains 1/8 max HP per turn. Makes physical attackers ineffective with constant HP drain, dangerous for bulky Pokémon.
- Poisoned: Same as 'burnt' - drains 1/8 max HP per turn.
- Paralized: Reduces Speed stat by 25%, with 25% chance to be fully immobilized and not be able to attack.
- Asleep: Prevents attacks/items for several turns. Sleep lasts for a randomly chosen duration of 1 to 5 turns.
- Frozen: Pokemon is unable to move. The Pokemon has 20% chance it will get thawed in the next turn. 

Given the above information, the below stats will help you take a move decision:

------------------------------------------------------------
1) Your pokemon's stats are...

<<< USER POKEMON STATS >>>
{user_stats}
<<< ------------------ >>>

2) Your foe's pokemon stats are...

<<< FOE POKEMON STATS >>>
{foe_stats}
<<< ------------

3) your pokemon's status is...

<<< USER STATUS >>>
{user_nvstatus}
<<< ----- >>>

4) your foe pokemon's status is...

<<< FOE STATUS >>>
{foe_nvstatus}
<<< ----- >>>
------------------------------------------------------------

Your pokemon's four possible moves are...

<<< MOVES >>>
{moves}
<<< ----- >>>

Which one do you choose? Answer in the following manner:
'<move>': '<motivation>'
"""
