import csv
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html

from src.types import pokemon_type_checker

def generate_radar(type1, type2=None):
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
    types = list(effectiveness_data.keys())  # List of all Pokémon types

    # Create a subplot layout with polar plots
    fig = make_subplots(
        rows=1, cols=2 if type2 else 1,
        subplot_titles=[f"{type1} Type Effectiveness", f"{type2} Type Effectiveness"] if type2 else [f"{type1} Type Effectiveness"],
        specs=[[{"type": "polar"}, {"type": "polar"}] if type2 else [{"type": "polar"}]]  # This specifies polar plots
    )

    # First type chart
    if type1 in effectiveness_data:
        df1 = pd.DataFrame({
            "Effectiveness": effectiveness_data[type1] + [effectiveness_data[type1][0]],  # Close the radar
            "Types": types + [types[0]]  # Close the radar
        })

        trace1 = go.Scatterpolar(
            r=df1["Effectiveness"],
            theta=df1["Types"],
            fill="toself",
            name=f"{type1} Type"
        )
        fig.add_trace(trace1, row=1, col=1)

    # Second type chart (if applicable)
    if type2 and type2 in effectiveness_data:
        df2 = pd.DataFrame({
            "Effectiveness": effectiveness_data[type2] + [effectiveness_data[type2][0]],  # Close the radar
            "Types": types + [types[0]]  # Close the radar
        })

        trace2 = go.Scatterpolar(
            r=df2["Effectiveness"],
            theta=df2["Types"],
            fill="toself",
            name=f"{type2} Type"
        )
        fig.add_trace(trace2, row=1, col=2)

    # Layout settings
    fig.update_layout(
        title_text="Pokémon Type Effectiveness Radar",
        showlegend=True
    )

    return fig

def pokemon_info(pokedex_number):
    print("Pokemon Info!")
    """
    Retrieves Pokémon information from the CSV using its Pokédex number.

    Args:
        pokedex_number: The Pokédex number of the Pokémon (integer).

    Returns:
        A tuple (pokemon_name, output, type1, type2) containing the Pokémon's name,
        formatted string with Pokémon info, and its type(s).
    """
    try:
        with open("151pokemon.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if int(row["pokedex"]) == pokedex_number:  # Match by Pokédex number
                    pokemon_name = row["pokemon"].upper()
                    type1 = row["type1"]
                    type2 = row["type2"] if row["type2"] else None

                    output = f"{pokemon_name} (Pokédex #{pokedex_number}) is a "

                    if type1 and type2:
                        output += f"{type1}/{type2} type Pokémon.\n"
                        type_info1 = pokemon_type_checker(type1)                   
                        type_info2 = pokemon_type_checker(type2)
                        if isinstance(type_info1, dict):
                            output += format_type_info(type1, type_info1)
                        else:
                            output += f"{type1}: {type_info1}\n"

                        if isinstance(type_info2, dict):
                            output += format_type_info(type2, type_info2)
                        else:
                            output += f"{type2}: {type_info2}\n"

                    elif type1:
                        output += f"{type1} type Pokémon.\n"
                        type_info = pokemon_type_checker(type1)
                        
                        if isinstance(type_info, dict):
                            output += format_type_info(type1, type_info)
                        else:
                            output += f"{type1}: {type_info}\n"

                    return pokemon_name, output, type1, type2

            return None, f"Pokémon with Pokédex number {pokedex_number} not found.\n", None, None

    except FileNotFoundError:
        return None, "Error: '151pokemon.csv' not found. Please make sure the file is in the same directory.", None, None
    except ValueError:
        return None, "Error: Invalid Pokédex number format. Please enter a number.", None, None

def format_type_info(type_name, type_info):
    strengths = type_info["strong"]
    weaknesses = type_info["weak"]
    no_effects = type_info["no_effect"]
    
    output = f"{type_name} is 2x effective against: "
    output += ", ".join(strengths) if strengths else "None"
    
    output += "\n"
    output += f"{type_name} is 0.5x effective against: "
    output += ", ".join(weaknesses) if weaknesses else "None"
    
    if no_effects:
        output += "\n"
        output += f"{type_name} has no effect on: "
        output += ", ".join(no_effects)
    
    output += "\n"
    return output
