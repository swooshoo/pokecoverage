import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from src.pokemon import pokemon_info, generate_radar

app = dash.Dash(__name__)

# Example function that can be called from main.py
def get_pokemon_data(pokedex_number):
    pokemon_name, info_output, type1, type2 = pokemon_info(pokedex_number)
    if not pokemon_name:
        return info_output, None
    return info_output, generate_radar(type1, type2)

# Dash app layout
app.layout = html.Div([
    html.H1("Pokémon Type Effectiveness"),
    
    # Input field for user to enter Pokédex number
    dcc.Input(id="pokemon-input", type="number", placeholder="Enter Pokédex number"),
    
    # Display Pokémon info
    html.Div(id="pokemon-info"),
    
    # Display radar chart
    dcc.Graph(id="radar-chart")
])

# Callback to update Pokémon info and radar chart based on input
@app.callback(
    [Output("pokemon-info", "children"), Output("radar-chart", "figure")],
    [Input("pokemon-input", "value")]
)
def display_pokemon_info(pokedex_number):
    if pokedex_number:
        info_output, radar_figure = get_pokemon_data(int(pokedex_number))
        return html.Div([html.Pre(info_output)]), radar_figure
    return "Enter a valid Pokémon Pokédex number.", {}

if __name__ == "__main__":
    app.run_server(debug=True)