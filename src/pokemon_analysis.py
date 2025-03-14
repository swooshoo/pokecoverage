"""
Pokemon Team Analysis Module

This module provides comprehensive functionality for Pokemon team analysis, including 
type effectiveness calculations, team metrics, and visualization tools.
"""

import csv
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Try to import pokemon_type_checker, with fallback for different import structures
try:
    from src.types import pokemon_type_checker
except ImportError:
    try:
        from types import pokemon_type_checker
    except ImportError:
        # Fallback function if the original can't be imported
        def pokemon_type_checker(type_name):
            return {"strong": [], "weak": [], "no_effect": []}


class PokemonData:
    """Class for accessing and manipulating Pokemon data."""
    
    @staticmethod
    def format_type_info(type_name, type_info):
        """
        Format type effectiveness information as a readable string.
        
        Args:
            type_name: The name of the type
            type_info: Dictionary with 'strong', 'weak', and 'no_effect' keys
            
        Returns:
            str: Formatted string with type effectiveness information
        """
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
    
    @staticmethod
    def get_pokemon_info(pokedex_number, pokemon_csv_path="151pokemon.csv"):
        """
        Retrieves Pokémon information from the CSV using its Pokédex number.

        Args:
            pokedex_number: The Pokédex number of the Pokémon (integer).
            pokemon_csv_path: Path to the Pokemon CSV file (defaults to "151pokemon.csv")

        Returns:
            A tuple (pokemon_name, output, type1, type2) containing the Pokémon's name,
            formatted string with Pokémon info, and its type(s).
        """
        try:
            with open(pokemon_csv_path, "r", encoding="utf-8") as file:
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
                                output += PokemonData.format_type_info(type1, type_info1)
                            else:
                                output += f"{type1}: {type_info1}\n"

                            if isinstance(type_info2, dict):
                                output += PokemonData.format_type_info(type2, type_info2)
                            else:
                                output += f"{type2}: {type_info2}\n"

                        elif type1:
                            output += f"{type1} type Pokémon.\n"
                            type_info = pokemon_type_checker(type1)
                            
                            if isinstance(type_info, dict):
                                output += PokemonData.format_type_info(type1, type_info)
                            else:
                                output += f"{type1}: {type_info}\n"

                        return pokemon_name, output, type1, type2

                return None, f"Pokémon with Pokédex number {pokedex_number} not found.\n", None, None

        except FileNotFoundError:
            return None, f"Error: '{pokemon_csv_path}' not found. Please make sure the file is in the correct directory.", None, None
        except ValueError:
            return None, "Error: Invalid Pokédex number format. Please enter a number.", None, None


class TeamAnalysis:
    """Class for analyzing Pokemon team composition and effectiveness."""
    
    @staticmethod
    def calculate_type_effectiveness(team_data, types_csv_path="types.csv"):
        """
        Calculate defensive and offensive effectiveness for a team of Pokémon.
        
        Args:
            team_data: List of dictionaries with Pokémon data (including types)
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
        
        Returns:
            tuple: (defensive_metrics, offensive_metrics)
        """
        # Load the type effectiveness data
        types_df = pd.read_csv(types_csv_path)
        
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
    
    @staticmethod
    def recommend_types_for_defense(vulnerable_types, defensive_metrics, types_csv_path="types.csv"):
        """
        Recommend Pokémon types that would help address defensive vulnerabilities.
        
        Args:
            vulnerable_types: List of types the team is vulnerable to
            defensive_metrics: Dictionary of defensive effectiveness values
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
            
        Returns:
            list: Recommended types to add for better defense
        """
        # Load the type effectiveness data
        types_df = pd.read_csv(types_csv_path)
        
        # Initialize counters for how well each type defends against vulnerable types
        type_defense_scores = {t: 0 for t in types_df['Type'].values}
        
        # For each vulnerable type, find types that resist it
        for v_type in vulnerable_types[:3]:  # Focus on top 3 vulnerabilities
            for def_type in type_defense_scores.keys():
                # Check how effective the vulnerable type is against this defensive type
                effectiveness = float(types_df.loc[types_df['Type'] == v_type, def_type].iloc[0])
                # If this type resists the vulnerable type, increase its score
                if effectiveness < 1.0:
                    type_defense_scores[def_type] += (1.0 - effectiveness) * 2
                # If this type is weak to the vulnerable type, decrease its score
                elif effectiveness > 1.0:
                    type_defense_scores[def_type] -= (effectiveness - 1.0)
        
        # Sort types by their defensive utility score
        recommended_types = sorted(type_defense_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 5 recommended types
        return [t[0] for t in recommended_types[:5]]
    
    @staticmethod
    def recommend_types_for_offense(offensive_gaps, offensive_metrics, types_csv_path="types.csv"):
        """
        Recommend Pokémon types that would help address offensive gaps.
        
        Args:
            offensive_gaps: List of types the team struggles to hit effectively
            offensive_metrics: Dictionary of offensive effectiveness values
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
            
        Returns:
            list: Recommended types to add for better offense
        """
        # Load the type effectiveness data
        types_df = pd.read_csv(types_csv_path)
        
        # Initialize counters for how well each type attacks the gap types
        type_offense_scores = {t: 0 for t in types_df['Type'].values}
        
        # For each offensive gap, find types that are super effective against it
        for gap_type in offensive_gaps[:3]:  # Focus on top 3 gaps
            for atk_type in type_offense_scores.keys():
                # Check how effective this attacking type is against the gap type
                effectiveness = float(types_df.loc[types_df['Type'] == atk_type, gap_type].iloc[0])
                # If this type is super effective against the gap type, increase its score
                if effectiveness > 1.0:
                    type_offense_scores[atk_type] += (effectiveness - 1.0) * 2
        
        # Sort types by their offensive utility score
        recommended_types = sorted(type_offense_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 5 recommended types
        return [t[0] for t in recommended_types[:5]]
    
    @staticmethod
    def calculate_team_kpis(team_data, types_csv_path="types.csv"):
        """
        Calculate team KPIs based on type effectiveness with specific type recommendations.
        
        Args:
            team_data: List of dictionaries with Pokémon data
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
            
        Returns:
            dict: Dictionary of KPI values and type recommendations
        """
        # Get raw type effectiveness
        defensive_metrics, offensive_metrics = TeamAnalysis.calculate_type_effectiveness(team_data, types_csv_path)
        all_types = list(defensive_metrics.keys())
        
        # Calculate defensive KPIs
        defensive_vulnerability = sum(defensive_metrics.values())
        
        # Calculate how many types the team resists
        types_resisted = sum(1 for v in defensive_metrics.values() if v < 0)
        team_coverage_score = (types_resisted / len(all_types)) * 100
        
        # Find types with poor defensive coverage (types team is vulnerable to)
        vulnerable_types = [t for t in all_types if defensive_metrics[t] > 0]
        vulnerable_types.sort(key=lambda t: defensive_metrics[t], reverse=True)
        
        # Count defensive holes (types where 3+ team members are weak)
        # This is a simplified approximation based on team size and vulnerability score
        team_size = len(team_data)
        defensive_holes = sum(1 for v in defensive_metrics.values() if v >= (team_size / 2))
        
        # Calculate offensive KPIs
        # Count types team can hit super effectively
        super_effective_count = sum(1 for v in offensive_metrics.values() if v > 0)
        type_coverage_index = (super_effective_count / len(all_types)) * 100
        
        # Find types with poor offensive coverage (types team struggles to hit)
        offensive_gaps = [t for t in all_types if offensive_metrics[t] <= -1]
        offensive_gaps.sort(key=lambda t: offensive_metrics[t])
        
        # Count unique types in team (for STAB diversity)
        unique_types = set()
        for pokemon in team_data:
            if pokemon.get('type1') and pokemon.get('type1') != 'None':
                unique_types.add(pokemon.get('type1'))
            if pokemon.get('type2') and pokemon.get('type2') != 'None':
                unique_types.add(pokemon.get('type2'))
        stab_diversity = len(unique_types)
        
        # Missing types (types not represented in the team)
        missing_types = set(all_types) - unique_types
        
        # Find recommended types to add based on overall analysis
        # 1. Types that would help address defensive vulnerabilities
        defensive_recommendations = TeamAnalysis.recommend_types_for_defense(vulnerable_types, defensive_metrics, types_csv_path)
        
        # 2. Types that would help address offensive gaps
        offensive_recommendations = TeamAnalysis.recommend_types_for_offense(offensive_gaps, offensive_metrics, types_csv_path)
        
        return {
            'defensive_metrics': defensive_metrics,
            'offensive_metrics': offensive_metrics,
            'defensive_vulnerability_index': defensive_vulnerability,
            'team_coverage_score': team_coverage_score,
            'defensive_holes': defensive_holes,
            'type_coverage_index': type_coverage_index,
            'stab_diversity': stab_diversity,
            'vulnerable_types': vulnerable_types[:3],  # Top 3 types team is weak to
            'offensive_gaps': offensive_gaps[:3],      # Top 3 types team struggles to hit
            'missing_types': list(missing_types),
            'defensive_recommendations': defensive_recommendations,
            'offensive_recommendations': offensive_recommendations
        }


class TeamVisualization:
    """Class for visualizing Pokemon team data."""
    
    @staticmethod
    def generate_radar_chart(team_data, types_csv_path="types.csv"):
        """
        Generate a radar chart for team type effectiveness.
        
        Args:
            team_data: List of dictionaries with Pokémon data
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
            
        Returns:
            plotly.graph_objects.Figure: Radar chart figure
        """
        # Calculate KPIs
        kpis = TeamAnalysis.calculate_team_kpis(team_data, types_csv_path)
        
        # Extract metrics for radar chart
        defensive_metrics = kpis['defensive_metrics']
        offensive_metrics = kpis['offensive_metrics']
        
        # Prepare data for radar chart
        types = list(defensive_metrics.keys())
        
        # Normalize metrics for better visualization
        max_def = max(abs(v) for v in defensive_metrics.values()) or 1
        max_off = max(abs(v) for v in offensive_metrics.values()) or 1
        
        # Convert metrics to lists with normalized values
        defensive_values = [defensive_metrics[t] / max_def for t in types]
        offensive_values = [offensive_metrics[t] / max_off for t in types]
        
        # Create radar chart
        fig = go.Figure()
        
        # Add defensive trace (lower is better for defense)
        fig.add_trace(go.Scatterpolar(
            r=[-v for v in defensive_values],  # Invert values since lower is better for defense
            theta=types,
            fill='toself',
            name='Defensive Effectiveness',
            line_color='#0D92F4',
            fillcolor='rgba(13, 146, 244, .2)'
        ))
        
        # Add offensive trace (higher is better for offense)
        fig.add_trace(go.Scatterpolar(
            r=offensive_values,
            theta=types,
            fill='toself',
            name='Offensive Effectiveness',
            line_color='#C62E2E',
            fillcolor='rgba(249, 84, 84, .2)'
        ))
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-1.5, 1.5],  # Adjusted range to accommodate normalized values
                    tickvals=[-1, -0.5, 0, 0.5, 1],  # Normalized position values for ticks
                    ticktext=["0.25×", "0.5×", "1×", "2×", "4×"],  # Keep the meaningful labels
                )
            ),
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def generate_bar_chart(team_data, types_csv_path="types.csv"):
        """
        Generate a bar chart showing team type effectiveness.
        
        Args:
            team_data: List of dictionaries with Pokémon data
            types_csv_path: Path to the types CSV file (defaults to "types.csv")
            
        Returns:
            plotly.graph_objects.Figure: Bar chart figure
        """
        # Calculate KPIs
        kpis = TeamAnalysis.calculate_team_kpis(team_data, types_csv_path)
        
        # Extract metrics for bar chart
        defensive_metrics = kpis['defensive_metrics']
        offensive_metrics = kpis['offensive_metrics']
        
        # Prepare data for bar chart
        types = list(defensive_metrics.keys())
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=types,
            y=list(defensive_metrics.values()),
            name='Defensive (lower is better)',
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            x=types,
            y=list(offensive_metrics.values()),
            name='Offensive (higher is better)',
            marker_color='red'
        ))
        
        # Update layout
        fig.update_layout(
            title="Team Type Effectiveness",
            xaxis_title="Types",
            yaxis_title="Effectiveness Score",
            barmode='group',
            showlegend=True
        )
        
        return fig


# Convenience functions for backwards compatibility

def pokemon_info(pokedex_number, pokemon_csv_path="151pokemon.csv"):
    """Backwards compatibility wrapper for PokemonData.get_pokemon_info"""
    return PokemonData.get_pokemon_info(pokedex_number, pokemon_csv_path)

def calculate_type_effectiveness(team_data, types_csv_path="types.csv"):
    """Backwards compatibility wrapper for TeamAnalysis.calculate_type_effectiveness"""
    return TeamAnalysis.calculate_type_effectiveness(team_data, types_csv_path)

def calculate_team_kpis(team_data, types_csv_path="types.csv"):
    """Backwards compatibility wrapper for TeamAnalysis.calculate_team_kpis"""
    return TeamAnalysis.calculate_team_kpis(team_data, types_csv_path)

def recommend_types_for_defense(vulnerable_types, defensive_metrics, types_csv_path="types.csv"):
    """Backwards compatibility wrapper for TeamAnalysis.recommend_types_for_defense"""
    return TeamAnalysis.recommend_types_for_defense(vulnerable_types, defensive_metrics, types_csv_path)

def recommend_types_for_offense(offensive_gaps, offensive_metrics, types_csv_path="types.csv"):
    """Backwards compatibility wrapper for TeamAnalysis.recommend_types_for_offense"""
    return TeamAnalysis.recommend_types_for_offense(offensive_gaps, offensive_metrics, types_csv_path)

def generate_radar(team_data, types_csv_path="types.csv"):
    """Backwards compatibility wrapper for TeamVisualization.generate_radar_chart"""
    return TeamVisualization.generate_radar_chart(team_data, types_csv_path)

def generate_bar(team_data, types_csv_path = "types.csv"):
    return TeamVisualization.generate_bar_chart(team_data,types_csv_path="types.csv")