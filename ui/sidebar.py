# Sidebar configuration and controls

import streamlit as st

def render_sidebar():
    """Render the sidebar with battle configuration controls."""
    st.sidebar.header("Battle Configuration")

    # Pokemon selection
    st.sidebar.subheader("Select Your Pokémon")
    user_pokemon_name = st.sidebar.text_input(
        "Enter your Pokémon name:", 
        value="charizard", 
        key="user_pkmn"
    )

    st.sidebar.subheader("Select Opponent Pokémon")
    foe_pokemon_name = st.sidebar.text_input(
        "Enter opponent Pokémon name:", 
        value="blastoise", 
        key="foe_pkmn"
    )

    # LLM Model selection
    st.sidebar.subheader("LLM Configuration")
    llm_model = st.sidebar.selectbox(
        "Select LLM Model:",
        ["openai:gpt-4o-mini", "openai:gpt-4", "openai:gpt-3.5-turbo"],
        help="Select the language model to use for battle decisions"
    )

    # Battle control
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    start_battle = col1.button("🏃‍♀️‍➡️ Load", key="start_btn", use_container_width=True)
    reset_battle = col2.button("🔄 Reset", key="reset_btn", use_container_width=True)

    return {
        "user_pokemon_name": user_pokemon_name,
        "foe_pokemon_name": foe_pokemon_name,
        "llm_model": llm_model,
        "start_battle": start_battle,
        "reset_battle": reset_battle,
    }

def handle_reset():
    """Handle reset button click."""
    st.session_state.battle_log = []
    st.session_state.battle_in_progress = False
    st.session_state.battle_result = None
    st.session_state.user_pokemon = None
    st.session_state.foe_pokemon = None
    st.rerun()
