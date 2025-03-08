import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback, Patch
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from src.pokemon import pokemon_info, generate_radar, calculate_team_kpis
import plotly.graph_objects as go

app = dash.Dash(__name__)

# Load Pokemon data
new_df = pd.read_csv("151pokemon.csv")

# Column definitions for AG Grid
newColDefs = [
    {"field": "pokedex"},
    {
        "field": "pokemon",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        "headerCheckboxSelectionFilteredOnly": True,
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
    html.H1("Pokémon Team Analysis Tool", style={'textAlign': 'center'}),
    
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
                style={'height': '400px', 'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3("Team Type Effectiveness"),
            dcc.Graph(id="radar-chart", style={'height': '400px'}),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        html.H3("Team Performance Metrics", style={'textAlign': 'center'}),
        html.Div(id="team-kpi-display", style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'})
    ], style={'marginTop': '20px'}),
    
    # Individual Pokemon lookup (original functionality)
    html.Div([
        html.H3("Individual Pokémon Lookup", style={'textAlign': 'center'}),
        dcc.Input(id="pokemon-input", type="number", placeholder="Enter Pokédex number"),
        html.Div(id="pokemon-info"),
    ], style={'marginTop': '30px', 'textAlign': 'center'}),
], style={'padding': '20px'})

# Callback to update radar chart based on selected Pokemon
@app.callback(
    [Output("radar-chart", "figure"), Output("team-kpi-display", "children")],
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def update_team_analysis(selected_rows):
    if not selected_rows or len(selected_rows) == 0:
        # Return empty figure and message if no Pokémon selected
        return {}, html.Div("Select Pokémon to see team metrics")
    
    # Limit to maximum 6 Pokémon (standard team size)
    team_data = selected_rows[:6]
    
    # Calculate team KPIs
    kpis = calculate_team_kpis(team_data)
    
    # Generate radar chart for the selected team
    radar_fig = generate_radar(team_data)
    
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
            html.P("Types that many team members are weak to")
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
    
    return radar_fig, kpi_cards

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

if __name__ == "__main__":
    app.run_server(debug=True)