# Battle execution logic

import streamlit as st
import logging
from io import StringIO

from src.pokemon.pokemon import Pokemon
from src.battlefield.battle_pokemon import BattlePokemon
from src.tools.tools import get_pokemon_attributes, return_loaded_pokemon_data
from src.battlefield.battle_engine import BattleEngine
from langchain.chat_models import init_chat_model

def run_battle(user_pokemon_name, foe_pokemon_name, llm_model):
    """Execute the battle between two Pokémon."""
    st.session_state.battle_in_progress = True
    st.session_state.battle_log = []
    st.session_state.battle_result = None

    user_pokemon, foe_pokemon = load_pokemons_in_display(user_pokemon_name, foe_pokemon_name)
    run_pokemon_battle(user_pokemon, foe_pokemon, llm_model)
    

def display_pokemon_info(user_pokemon: Pokemon, foe_pokemon: Pokemon):
    """Display Pokémon information before battle."""
    st.markdown("---")
    st.markdown("### ⚡ Battle Matchup")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Your Pokémon")
        st.markdown(pokemon_info_markdown(user_pokemon))
        st.image(user_pokemon.sprite_front_url, width=120)
    
    with col2:
        st.markdown("### 🔥 Opponent Pokémon")
        st.markdown(pokemon_info_markdown(foe_pokemon))
        st.image(foe_pokemon.sprite_front_url, width=120)

def pokemon_info_markdown(pokemon: Pokemon) -> str:
    """Generate markdown string for Pokémon info."""
    return f"""
    **Name:** {pokemon.name.upper()}  
    **Level:** {pokemon.level}  
    **Type(s):** {', '.join(pokemon.types)}  
    **HP:** {int(pokemon.stats.hp)}  
    **Attack:** {int(pokemon.stats.attack)}  
    **Defense:** {int(pokemon.stats.defense)}  
    **Sp. Atk:** {int(pokemon.stats.special_attack)}  
    **Sp. Def:** {int(pokemon.stats.special_defense)}  
    **Speed:** {int(pokemon.stats.speed)}  
    **Moves:** {', '.join([m.name for m in pokemon.moves])}
    """

def load_pokemons_in_display(user_pokemon_name, foe_pokemon_name):
    """Execute the battle between two Pokémon."""
    with st.spinner("Loading Pokémon data..."):
        try:
            # Get Pokemon attributes
            pokemon_data = get_pokemon_attributes(
                [user_pokemon_name.lower(), foe_pokemon_name.lower()]
            )
            pokemon_list = return_loaded_pokemon_data(pokemon_data)
            
            # Match Pokemon by name
            user_pokemon: BattlePokemon = next(
                (p for p in pokemon_list if p.name.lower() == user_pokemon_name.lower()),
                None
            )
            foe_pokemon: BattlePokemon = next(
                (p for p in pokemon_list if p.name.lower() == foe_pokemon_name.lower()),
                None
            )
            
            if user_pokemon is None or foe_pokemon is None:
                st.error(f"❌ Could not find Pokémon. Please check the names and try again.")
                st.session_state.battle_in_progress = False
                return
            
            # Display Pokemon info
            display_pokemon_info(user_pokemon, foe_pokemon)
            return user_pokemon, foe_pokemon

        except Exception as e:
            st.error(f"❌ Error loading Pokémon data: {str(e)}")
            st.session_state.battle_in_progress = False

def run_pokemon_battle(user_pokemon: BattlePokemon, foe_pokemon: BattlePokemon, llm_model: str):
    """Run the Pokémon battle and update session state."""
    st.markdown("---")
    st.markdown("### ⚡ Battle History")
    # Initialize LLM
    with st.spinner("Initializing LLM..."):
        try:
            llm = init_chat_model(model=llm_model)
        except Exception as e:
            st.error(f"❌ Error initializing LLM: {str(e)}")
            st.session_state.battle_in_progress = False
            return
    
    # Capture logs
    log_capture_string = StringIO()
    log_handler = logging.StreamHandler(log_capture_string)
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    log_handler.setFormatter(formatter)
    
    logger = logging.getLogger('config.logging')
    logger.addHandler(log_handler)
    
    # Run the battle
    try:
        with st.spinner("Battle in progress..."):
            battle_engine = BattleEngine(
                user_pokemon=user_pokemon,
                foe_pokemon=foe_pokemon,
                llm=llm
            )
            battle_engine.start_ai_battle()
            # Store Pokemon in session
            st.session_state.user_pokemon = battle_engine.user_pokemon
            st.session_state.foe_pokemon = battle_engine.foe_pokemon

        # Get the logs
        log_contents = log_capture_string.getvalue()
        st.session_state.battle_log = log_contents.split('\n')
        
        # Determine winner
        if battle_engine.user_pokemon.is_alive:
            st.session_state.battle_result = f"🏆 {user_pokemon.name.upper()} wins the battle! 🏆"
        else:
            st.session_state.battle_result = f"🏆 {foe_pokemon.name.upper()} wins the battle! 🏆"
        
    except Exception as e:
        st.error(f"❌ Error during battle: {str(e)}")
        st.session_state.battle_log.append(f"Error: {str(e)}")
    finally:
        logger.removeHandler(log_handler)
        st.session_state.battle_in_progress = False