import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
from src.pokemon import pokemon_info, generate_radar

from dash import Patch
import pandas as pd

app = dash.Dash(__name__)

df = pd.read_csv("151pokemon.csv")

newColDefs = [
    {"field": "pokedex"},
    {"field": "pokemon"},
    {"field": "type1"},
    {"field": "type2"},
]

app.layout = html.Div([
    dcc.Store(id='my-store'),
    dag.AgGrid(
            id="selected-pokemon",
            columnDefs=newColDefs,
            rowData=df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False, "rowMultiSelectWithClick" : True},
            selectedRows=df.head(5).to_dict("records"),
        ),
    html.Pre(id="pre-row-selection-selected-rows", style={'text-wrap': 'wrap'}),
    html.Div(id='current-store')    
])

@callback(
    Output("pre-row-selection-selected-rows", "children"),
    Input("selected-pokemon", "selectedRows"),
)
def output_selected_rows(selected_rows):
    selected_list = [f"{s['pokemon']} (#{s['pokedex']})" for s in selected_rows]
    return f"You selected the pokemon {'s' if len(selected_rows) > 1 else ''}:\n{', '.join(selected_list)}" if selected_rows else "No selections"

def update_store(value):
    return value

# @app.callback(
#     Output('current-store', 'children'),
#     Input('my-store', 'modified_timestamp'),
#     State('my-store', 'data')
# )
# def display_store_info(timestamp, data):
#     return f"The store currently contains {data}, timestamp: {timestamp}"

if __name__ == "__main__":
    app.run_server(debug=True)
