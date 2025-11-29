# Battle result display components

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def create_hp_chart_with_hover(history_data, pokemon_name):
    """
    Create an interactive Plotly chart with hover metadata.
    
    Args:
        history_data: Dictionary with "Round", "HP", and other metadata columns
        pokemon_name: Name of the Pokémon for the title
    
    Returns:
        Plotly Figure object
    """
    # Convert to DataFrame if it's a dict
    if isinstance(history_data, dict):
        df = pd.DataFrame(history_data)
    else:
        df = history_data
    
    # Build hover text with all available columns
    hover_text = []
    for idx, row in df.iterrows():
        hover_info = f"<b>{row['Round']}</b><br>"
        hover_info += f"HP: {int(row['HP'])}<br>"
        
        # Add all other columns as metadata
        for col in df.columns:
            if col not in ['Round', 'HP']:
                hover_info += f"{col}: {row[col]}<br>"
        
        hover_text.append(hover_info)
    
    # Create the Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Round'],
        y=df['HP'],
        mode='lines+markers',
        name='HP',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8),
        hovertext=hover_text,
        hoverinfo='text',
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.2)'
    ))
    
    # Update layout for better appearance
    fig.update_layout(
        title=f"{pokemon_name.capitalize()} HP Over Time",
        xaxis_title="Round",
        yaxis_title="HP",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray'),
    )
    
    return fig

def display_battle_log():
    """Display the battle log if available."""
    if st.session_state.battle_log:
        st.markdown("### Battle Progress")
        log_text = "\n".join(st.session_state.battle_log)
        col1, col2 = st.columns(2)
            
        with col1:
            with st.container():
                user_chart = create_hp_chart_with_hover(
                    st.session_state.user_pokemon.history,
                    st.session_state.user_pokemon.name
                )
                st.plotly_chart(user_chart, use_container_width=True)
        
        with col2:
            with st.container():
                foe_chart = create_hp_chart_with_hover(
                    st.session_state.foe_pokemon.history,
                    st.session_state.foe_pokemon.name
                )
                st.plotly_chart(foe_chart, use_container_width=True)

def display_battle_result():
    """Display the battle result and final stats."""
    if st.session_state.battle_result:
        st.success(st.session_state.battle_result)
        
        # Display final stats
        if st.session_state.user_pokemon and st.session_state.foe_pokemon:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### {st.session_state.user_pokemon.name.upper()}
                - **HP Remaining:** {int(st.session_state.user_pokemon.current_hp)}/{int(st.session_state.user_pokemon.stats.hp)}
                - **Status:** {'Alive' if st.session_state.user_pokemon.is_alive else 'Fainted'}
                - **Status Condition:** {st.session_state.user_pokemon.nvstatus.value}
                """)
            
            with col2:
                st.markdown(f"""
                ### {st.session_state.foe_pokemon.name.upper()}
                - **HP Remaining:** {int(st.session_state.foe_pokemon.current_hp)}/{int(st.session_state.foe_pokemon.stats.hp)}
                - **Status:** {'Alive' if st.session_state.foe_pokemon.is_alive else 'Fainted'}
                - **Status Condition:** {st.session_state.foe_pokemon.nvstatus.value}
                """)

def display_footer():
    """Display footer information."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px;">
    
    </div>
    """, unsafe_allow_html=True)
