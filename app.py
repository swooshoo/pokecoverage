import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback, Patch
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from src.pokemon_analysis import PokemonData, TeamAnalysis, TeamVisualization
from src.pokemon_analysis import calculate_team_kpis, generate_radar, pokemon_info, generate_bar, generate_team_summary

app = dash.Dash(__name__)

# Load Pokemon data
new_df = pd.read_csv("151pokemon.csv")

# Column definitions for AG Grid
newColDefs = [
    {"field": "pokedex"},
    {
        "field": "pokemon",
        "headerCheckboxSelection": True,
    },
    {"field": "type1"},
    {"field": "type2"},
]

# Example function that can be called from main.py for individual Pokemon
def get_pokemon_data(pokedex_number):
    pokemon_name, info_output, type1, type2 = pokemon_info(pokedex_number)
    if not pokemon_name:
        return info_output, None
    # This would need to be updated to work with the new generate_radar function
    return info_output, {}

# Dash app layout
app.layout = html.Div([
    html.H1("Pokémon Team Diagnostic", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.H3("Select Your Pokémon Team (up to 6)"),
            dcc.Input(id="input-radio-row-selection-checkbox-header-filtered-only", 
                     placeholder="Quick filter...",
                     style={'marginBottom': '10px', 'width': '100%'}),
            dag.AgGrid(
                id="row-selection-checkbox-header-filtered-only",
                columnDefs=newColDefs,
                rowData=new_df.to_dict("records"),
                columnSize="sizeToFit",
                defaultColDef={"filter": True},
                dashGridOptions={"rowSelection": "multiple", "animateRows": False, "rowMultiSelectWithClick" : True},
                rowStyle= {"cursor": "pointer"},
                style={'height': '450px', 'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3("Team Type Effectiveness"),
            dcc.Graph(id="radar-chart", style={'height': '450px'}),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        html.H3("Selected Team", style={'textAlign': 'center'}),
        html.Div(id="selected-pokemon-display", style={
            'display': 'flex', 
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '10px',
            'marginTop': '10px'
        })
    ], style={'width': '100%', 'marginTop': '20px', 'marginBottom': '20px'}),
    
    
    html.Div([
        html.H3("Team Performance Metrics", style={'textAlign': 'center'}),
        html.Div(id="team-kpi-display", style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'})
    ], style={'marginTop': '20px'}),
    
    html.Div([
        html.H3("Team Type Recommendations", style={'textAlign': 'center'}),
        html.Div(id="team-recommendations", style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'})
    ], style={'marginTop': '30px'}),
    
    # Individual Pokemon lookup (original functionality)
    html.Div([
        html.H3("Individual Pokémon Lookup", style={'textAlign': 'center'}),
        dcc.Input(id="pokemon-input", type="number", placeholder="Enter Pokédex #"),
        html.Div(id="pokemon-info"),
    ], style={'marginTop': '30px', 'textAlign': 'center'}),
], style={'padding': '20px'})

# Callback to update radar chart based on selected Pokemon
@app.callback(
    [Output("radar-chart", "figure"), 
     Output("team-kpi-display", "children"),
     Output("team-recommendations", "children")],  # 3 outputs declared
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def update_team_analysis(selected_rows):
    if not selected_rows or len(selected_rows) == 0:
        # Return empty figure and message if no Pokémon selected
        return {}, html.Div("Select Pokémon to see team metrics"), html.Div("Select Pokémon to see type recommendations")
    
    
    # Limit to maximum 6 Pokémon (standard team size)
    team_data = selected_rows[:6]
    
    # Calculate team KPIs
    kpis = calculate_team_kpis(team_data)
    
    # Generate radar chart for the selected team
    bar_fig = generate_bar(team_data) #unused bar fig for offensive/defensive type effectiveness
    radar_fig = generate_radar(team_data)
    
    
    team_summary = generate_team_summary(team_data)  # Import this function
    
    summary_card = html.Div([ #initialize summary card
        html.H4("Team Analysis", style={'color': '#722ed1'}),
        html.P(team_summary, style={'lineHeight': '1.5', 'fontSize': '16px'})
    ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
    
    # Create KPI cards
    kpi_cards = [
        html.Div([
            html.H4("Defensive Coverage"),
            html.H2(f"{kpis['team_coverage_score']:.1f}%"),
            html.P("Types resisted by at least one team member")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#e6f7ff', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("Defensive Holes"),
            html.H2(f"{kpis['defensive_holes']}"),
            html.P("Types that team is weak to")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#fff1f0', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("Type Coverage"),
            html.H2(f"{kpis['type_coverage_index']:.1f}%"),
            html.P("Types your team can hit super effectively")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f6ffed', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("STAB Diversity"),
            html.H2(f"{kpis['stab_diversity']}"),
            html.P("Unique types in your team's composition")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#fff8f0', 'borderRadius': '5px', 'width': '22%'})
    ]

    # Create recommendation cards
    recommendation_cards = html.Div([
        # First card: vulnerabilities
        html.Div([
            html.H4("Defensive Holes", style={'color': '#cf1322'}),
            html.P("Your team is most vulnerable to these types:"),
            html.Div([
                html.Span(type_name, style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#ffccc7',
                    'borderRadius': '15px',
                    'color': '#cf1322'
                }) for type_name in kpis.get('vulnerable_types', [])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        
        # Second card: offensive gaps
        html.Div([
            html.H4("Offensive Holes", style={'color': '#d46b08'}),
            html.P("Your team struggles to hit these types:"),
            html.Div([
                html.Span(type_name, style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#ffe7ba',
                    'borderRadius': '15px',
                    'color': '#d46b08'
                }) for type_name in kpis.get('offensive_gaps', [])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        
        # Third card: recommended types
        html.Div([
            html.H4("Recommended Types", style={'color': '#1890ff'}),
            html.P("Add Pokémon with these types to improve your team:"),
            html.Div([
                # Defensive recommendations
                html.Div([
                    html.H5("For Defense:", style={'margin': '5px 0'}),
                    html.Div([
                        html.Span(type_name, style={
                            'display': 'inline-block',
                            'margin': '3px',
                            'padding': '5px 10px',
                            'backgroundColor': '#e6f7ff',
                            'borderRadius': '15px',
                            'color': '#1890ff'
                        }) for type_name in kpis.get('defensive_recommendations', [])[:3]
                    ])
                ]),
                # Offensive recommendations
                html.Div([
                    html.H5("For Offense:", style={'margin': '5px 0'}),
                    html.Div([
                        html.Span(type_name, style={
                            'display': 'inline-block',
                            'margin': '3px',
                            'padding': '5px 10px',
                            'backgroundColor': '#f6ffed',
                            'borderRadius': '15px',
                            'color': '#52c41a'
                        }) for type_name in kpis.get('offensive_recommendations', [])[:3]
                    ])
                ])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        summary_card,
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})
    
    return radar_fig, kpi_cards, recommendation_cards

# Callback to filter Pokemon list
@app.callback(
    Output("row-selection-checkbox-header-filtered-only", "dashGridOptions"),
    Input("input-radio-row-selection-checkbox-header-filtered-only", "value"),
)
def update_filter(filter_value):
    gridOptions_patch = Patch()
    gridOptions_patch["quickFilterText"] = filter_value
    return gridOptions_patch

# Callback to update individual Pokemon info (original functionality)
@app.callback(
    [Output("pokemon-info", "children")],
    [Input("pokemon-input", "value")]
)
def display_pokemon_info(pokedex_number):
    if pokedex_number:
        info_output, _ = get_pokemon_data(int(pokedex_number))
        return [html.Div([html.Pre(info_output)])]
    return ["Enter a valid Pokémon Pokédex number."]

@app.callback(
    Output("selected-pokemon-display", "children"),
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def update_selected_pokemon_display(selected_rows):
    if not selected_rows or len(selected_rows) == 0:
        return html.Div("No Pokémon selected yet. Select up to 6 Pokémon for your team.", 
                       style={'textAlign': 'center', 'color': '#999'})
    
    team_data = selected_rows[:6]  # Limit to 6 Pokémon
    
    pokemon_cards = []
    for pokemon in team_data:
        # Create a card for each selected Pokémon
        pokemon_number = int(pokemon.get('pokedex', 0))
        pokemon_name = pokemon.get('pokemon', 'Unknown')
        type1 = pokemon.get('type1', '')
        type2 = pokemon.get('type2', '')
        
        # Get type colors
        type_colors = {
            'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0', 'Electric': '#F8D030',
            'Grass': '#78C850', 'Ice': '#98D8D8', 'Fighting': '#C03028', 'Poison': '#A040A0',
            'Ground': '#E0C068', 'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
            'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8', 'Dark': '#705848',
            'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
        }
        
        type1_color = type_colors.get(type1, '#AAAAAA')
        type2_color = type_colors.get(type2, '#AAAAAA')
        
        # Sprite URL (using PokeAPI sprites)
        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_number}.png"
        
        card = html.Div([
            html.Img(src=sprite_url, style={'width': '96px', 'height': '96px'}),
            html.Div(pokemon_name, style={'fontWeight': 'bold', 'marginTop': '5px'}),
            html.Div([
                html.Span(type1, style={
                    'backgroundColor': type1_color,
                    'color': 'white',
                    'padding': '2px 8px',
                    'borderRadius': '10px',
                    'fontSize': '12px',
                    'marginRight': '5px' if type2 else '0px'
                }),
                html.Span(type2, style={
                    'backgroundColor': type2_color,
                    'color': 'white',
                    'padding': '2px 8px',
                    'borderRadius': '10px',
                    'fontSize': '12px',
                    'display': 'inline-block' if type2 else 'none'
                })
            ], style={'marginTop': '5px'})
        ], style={
            'width': '120px',
            'textAlign': 'center',
            'padding': '10px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        })
        
        pokemon_cards.append(card)
    
    return pokemon_cards

if __name__ == "__main__":
    app.run_server(debug=True)