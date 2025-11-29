import streamlit as st
import sys
import os
from dotenv import load_dotenv


from pathlib import Path
# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UI modules
from ui.config import configure_page, apply_custom_css, initialize_session_state
from sidebar import render_sidebar, handle_reset
from battle_runner import run_battle
from display import display_battle_log, display_battle_result, display_footer

# Load environment variables
load_dotenv()

# Configure page and styling
configure_page()
apply_custom_css()
initialize_session_state()

# Title with logo
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    image_path = Path("ui/resources/emerald_logo.png")
    st.image(image_path, width='content')
    st.markdown("<div class='battle-header'>Pokémon AI Battle Simulator</div>", unsafe_allow_html=True)

# Render sidebar and get controls
sidebar_data = render_sidebar()

# Handle reset button
if sidebar_data["reset_battle"]:
    handle_reset()

# Handle start battle button
if sidebar_data["start_battle"] and not st.session_state.battle_in_progress:
    run_battle(
        sidebar_data["user_pokemon_name"],
        sidebar_data["foe_pokemon_name"],
        sidebar_data["llm_model"]
    )

# Display battle results
display_battle_log()
display_battle_result()
display_footer()
