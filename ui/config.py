# Streamlit page configuration and styling

import streamlit as st

def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Pokémon Battle Simulator",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling to the app."""
    st.markdown("""
        <style>
        .battle-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin: 20px 0;
        }
        .pokemon-card {
            border: 2px solid #FF6B6B;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            min-width: 300px;
        }
        .battle-log {
            background-color: #f0f0f0;
            border-radius: 5px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            border: 1px solid #ddd;
        }
        .battle-header {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #00d062;
            margin: 20px 0;
        }
        </style>
        """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        "battle_log": [],
        "battle_in_progress": False,
        "battle_result": None,
        "user_pokemon": None,
        "foe_pokemon": None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
