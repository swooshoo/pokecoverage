import numpy as np
import plotly.express as px
import pandas as pd

# Define Pokémon types
types = [
    'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 
    'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
]

# Type effectiveness dictionary
effectiveness_data = {
    'Normal':   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0, 1, 1, 0.5, 1],
    'Fire':     [1, 0.5, 0.5, 1, 2, 2, 1, 1, 1, 1, 1, 2, 0.5, 1, 0.5, 1, 2, 1],
    'Water':    [1, 2, 0.5, 1, 0.5, 1, 1, 1, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, 1],
    'Electric': [1, 1, 2, 0.5, 0.5, 1, 1, 1, 0, 2, 1, 1, 1, 1, 0.5, 1, 1, 1],
    'Grass':    [1, 0.5, 2, 1, 0.5, 1, 1, 0.5, 2, 0.5, 1, 0.5, 2, 1, 0.5, 1, 0.5, 1],
    'Ice':      [1, 0.5, 0.5, 1, 2, 0.5, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 0.5, 1],
    'Fighting': [2, 1, 1, 1, 1, 2, 1, 0.5, 1, 0.5, 0.5, 0.5, 2, 0, 1, 2, 2, 0.5],
    'Poison':   [1, 1, 1, 1, 2, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 0, 2],
    'Ground':   [1, 2, 1, 2, 0.5, 1, 1, 2, 1, 0, 1, 0.5, 2, 1, 1, 1, 2, 1],
    'Flying':   [1, 1, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 0.5, 1],
    'Psychic':  [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0.5, 1, 1, 1, 1, 0, 0.5, 1],
    'Bug':      [1, 0.5, 1, 1, 2, 1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 0.5, 1, 2, 0.5, 0.5],
    'Rock':     [1, 2, 1, 1, 1, 2, 0.5, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 0.5, 1],
    'Ghost':    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 1],
    'Dragon':   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0.5, 0],
    'Dark':     [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 0.5],
    'Steel':    [1, 0.5, 0.5, 0.5, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0.5, 2],
    'Fairy':    [1, 0.5, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1]
}

def generate_radar(type1, type2=None):
    """
    Generates radar charts for a Pokémon's type effectiveness.
    
    Args:
        type1 (str): Primary type of the Pokémon.
        type2 (str, optional): Secondary type of the Pokémon.
    """

    # Generate a radar chart for the first type
    if type1 in effectiveness_data:
        df1 = pd.DataFrame({
            "Effectiveness": effectiveness_data[type1] + [effectiveness_data[type1][0]],  # Close the radar
            "Types": types + [types[0]]  # Close the radar
        })

        fig1 = px.line_polar(df1, r="Effectiveness", theta="Types", line_close=True, title=f"{type1} Type Effectiveness")
        fig1.update_traces(fill="toself")
        fig1.show()

    # Generate a radar chart for the second type (if it exists)
    if type2 and type2 in effectiveness_data:
        df2 = pd.DataFrame({
            "Effectiveness": effectiveness_data[type2] + [effectiveness_data[type2][0]],  # Close the radar
            "Types": types + [types[0]]  # Close the radar
        })

        fig2 = px.line_polar(df2, r="Effectiveness", theta="Types", line_close=True, title=f"{type2} Type Effectiveness")
        fig2.update_traces(fill="toself")
        fig2.show()
