import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback, Patch
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
from src.pokemon import pokemon_info, generate_radar

from dash import Patch
import pandas as pd

app = dash.Dash(__name__)

#example dataset column defined
# example_df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
# )

# columnDefs = [
#     {
#         "field": "athlete",
#         "checkboxSelection": True,
#         "headerCheckboxSelection": True,
#         "headerCheckboxSelectionFilteredOnly": True,
#     },
#     {"field": "age"},
#     {"field": "country"},
#     {"field": "year"},
#     {"field": "sport"},
#     {"field": "total"},
# ]

new_df = pd.read_csv("151pokemon.csv")

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
    dcc.Graph(id="radar-chart"),
    
    dcc.Input(id="input-radio-row-selection-checkbox-header-filtered-only", placeholder="Quick filter..."),
        dag.AgGrid(
            id="row-selection-checkbox-header-filtered-only",
            columnDefs=newColDefs,
            rowData=new_df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False},
        ),
    ],
)

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

@app.callback(
    Output("row-selection-checkbox-header-filtered-only", "dashGridOptions"),
    Input("input-radio-row-selection-checkbox-header-filtered-only", "value"),
)
def update_filter(filter_value):
    gridOptions_patch = Patch()
    gridOptions_patch["quickFilterText"] = filter_value
    return gridOptions_patch

if __name__ == "__main__":
    app.run_server(debug=True)