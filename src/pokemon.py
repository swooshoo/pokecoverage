import csv
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.types import pokemon_type_checker

# Load the type effectiveness data
types_df = pd.read_csv("types.csv")

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

def calculate_type_effectiveness(team_data):
    """
    Calculate defensive and offensive effectiveness for a team of Pokémon.
    
    Args:
        team_data: List of dictionaries with Pokémon data (including types)
    
    Returns:
        tuple: (defensive_metrics, offensive_metrics)
    """
    # Load the type effectiveness data
    types_df = pd.read_csv("types.csv")
    
    # Determine column names dynamically
    # First column should be "Type" containing the attacking types
    attacking_col = "Type"
    # Remaining columns are the defending types
    defending_types = [col for col in types_df.columns if col != attacking_col]
    
    # Initialize metrics dictionaries for all types
    all_types = defending_types
    
    defensive_metrics = {t: 0 for t in all_types}
    offensive_metrics = {t: 0 for t in all_types}
    
    # For each Pokémon in the team
    for pokemon in team_data:
        type1 = pokemon.get('type1')
        type2 = pokemon.get('type2')
        
        # Skip if type1 is None or empty
        if not type1 or type1 == 'None':
            continue
            
        # Calculate defensive effectiveness (how vulnerable team is to each type)
        try:
            # Get type1 defensive multipliers (how effective each type is against this type)
            # We need to look at the column for this type across all attacking types
            type1_defense = {}
            for attacking_type in all_types:
                # Get how effective 'attacking_type' is against 'type1'
                type1_defense[attacking_type] = float(types_df.loc[types_df[attacking_col] == attacking_type, type1].iloc[0])
            
            # For dual-type Pokémon, calculate combined effectiveness
            if type2 and type2 != 'None':
                type2_defense = {}
                for attacking_type in all_types:
                    # Get how effective 'attacking_type' is against 'type2'
                    type2_defense[attacking_type] = float(types_df.loc[types_df[attacking_col] == attacking_type, type2].iloc[0])
                
                # Multiply effectiveness values to get combined effectiveness
                for t in all_types:
                    combined_value = type1_defense[t] * type2_defense[t]
                    
                    # Add weighted value to defensive metrics
                    # 4x weakness (2), 2x weakness (1), neutral (0), 0.5x resist (-1), 0.25x resist (-2), immune (-3)
                    if combined_value == 4.0:
                        defensive_metrics[t] += 2
                    elif combined_value == 2.0:
                        defensive_metrics[t] += 1
                    elif combined_value == 1.0:
                        defensive_metrics[t] += 0
                    elif combined_value == 0.5:
                        defensive_metrics[t] += -1
                    elif combined_value == 0.25:
                        defensive_metrics[t] += -2
                    elif combined_value == 0:
                        defensive_metrics[t] += -3
            else:
                # Single-type Pokémon
                for t in all_types:
                    value = type1_defense[t]
                    if value == 2.0:
                        defensive_metrics[t] += 1
                    elif value == 1.0:
                        defensive_metrics[t] += 0
                    elif value == 0.5:
                        defensive_metrics[t] += -1
                    elif value == 0:
                        defensive_metrics[t] += -3
        except Exception as e:
            print(f"Error processing defensive metrics for {type1}/{type2}: {e}")
        
        # Calculate offensive effectiveness (how well this Pokémon hits each type)
        # Using STAB as a proxy for offensive capability
        try:
            # Get types that this Pokémon hits super effectively with STAB from its first type
            if type1 and type1 != 'None':
                type1_row = types_df.loc[types_df[attacking_col] == type1].iloc[0]
                for t in all_types:
                    value = float(type1_row[t])
                    if value == 2.0:
                        offensive_metrics[t] += 1
                    elif value == 0.5:
                        offensive_metrics[t] += -1
                    elif value == 0:
                        offensive_metrics[t] += -3
                        
            # Add STAB coverage from second type if present
            if type2 and type2 != 'None':
                type2_row = types_df.loc[types_df[attacking_col] == type2].iloc[0]
                for t in all_types:
                    value = float(type2_row[t])
                    if value == 2.0:
                        offensive_metrics[t] += 1
                    elif value == 0.5:
                        offensive_metrics[t] += -1
                    elif value == 0:
                        offensive_metrics[t] += -3
        except Exception as e:
            print(f"Error processing offensive metrics for {type1}/{type2}: {e}")
    
    return defensive_metrics, offensive_metrics

def calculate_team_kpis(team_data):
    """
    Calculate team KPIs based on type effectiveness.
    
    Args:
        team_data: List of dictionaries with Pokémon data
        
    Returns:
        dict: Dictionary of KPI values
    """
    # Get raw type effectiveness
    defensive_metrics, offensive_metrics = calculate_type_effectiveness(team_data)
    all_types = defensive_metrics.keys()
    
    # Calculate defensive KPIs
    defensive_vulnerability = sum(defensive_metrics.values())
    
    # Calculate how many types the team resists
    types_resisted = sum(1 for v in defensive_metrics.values() if v < 0)
    team_coverage_score = (types_resisted / len(all_types)) * 100
    
    # Count defensive holes (types where 3+ team members are weak)
    # This is a simplified approximation based on team size and vulnerability score
    team_size = len(team_data)
    defensive_holes = sum(1 for v in defensive_metrics.values() if v >= (team_size / 2))
    
    # Calculate offensive KPIs
    # Count types team can hit super effectively
    super_effective_count = sum(1 for v in offensive_metrics.values() if v > 0)
    type_coverage_index = (super_effective_count / len(all_types)) * 100
    
    # Count unique types in team (for STAB diversity)
    unique_types = set()
    for pokemon in team_data:
        if pokemon.get('type1') and pokemon.get('type1') != 'None':
            unique_types.add(pokemon.get('type1'))
        if pokemon.get('type2') and pokemon.get('type2') != 'None':
            unique_types.add(pokemon.get('type2'))
    stab_diversity = len(unique_types)
    
    return {
        'defensive_metrics': defensive_metrics,
        'offensive_metrics': offensive_metrics,
        'defensive_vulnerability_index': defensive_vulnerability,
        'team_coverage_score': team_coverage_score,
        'defensive_holes': defensive_holes,
        'type_coverage_index': type_coverage_index,
        'stab_diversity': stab_diversity
    }

def generate_radar(team_data):
    """
    Generate a radar chart for team type effectiveness.
    
    Args:
        team_data: List of dictionaries with Pokémon data
        
    Returns:
        plotly.graph_objects.Figure: Radar chart figure
    """
    # Calculate KPIs
    kpis = calculate_team_kpis(team_data)
    
    # Extract metrics for radar chart
    defensive_metrics = kpis['defensive_metrics']
    offensive_metrics = kpis['offensive_metrics']
    
    # Prepare data for radar chart
    types = list(defensive_metrics.keys())
    
    # Normalize metrics for better visualization
    max_def = max(abs(v) for v in defensive_metrics.values()) or 1
    max_off = max(abs(v) for v in offensive_metrics.values()) or 1
    
    # Convert metrics to lists with normalized values
    defensive_values = [defensive_metrics[t] / max_def * 10 for t in types]
    offensive_values = [offensive_metrics[t] / max_off * 10 for t in types]
    
    # Create radar chart
    fig = go.Figure()
    
    # Add defensive trace (lower is better for defense)
    fig.add_trace(go.Scatterpolar(
        r=[-v for v in defensive_values],  # Invert values since lower is better for defense
        theta=types,
        fill='toself',
        name='Defensive Effectiveness',
        line_color='blue',
        fillcolor='rgba(0, 0, 255, 0.2)'
    ))
    
    # Add offensive trace (higher is better for offense)
    fig.add_trace(go.Scatterpolar(
        r=offensive_values,
        theta=types,
        fill='toself',
        name='Offensive Effectiveness',
        line_color='red',
        fillcolor='rgba(255, 0, 0, 0.2)'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-10, 10]  # Symmetric range for both metrics
            )
        ),
        title="Team Type Effectiveness",
        showlegend=True
    )
    
    return fig