import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pathlib import Path

from plots_layout import *

app = dash.Dash(__name__)

app.title = 'Share Trade Flows'

#for heroku to run correctly
server = app.server

input_path = Path('data/')

mex_imp_df = pd.read_csv(input_path / f'mex_import.csv')
mex_exp_df = pd.read_csv(input_path / f'mex_export.csv')
kor_imp_df = pd.read_csv(input_path / f'kor_import.csv')
kor_exp_df = pd.read_csv(input_path / f'kor_export.csv')
mex_imp_df = mex_imp_df[mex_imp_df['origin_name'] != 'EU27']
mex_exp_df = mex_exp_df[mex_exp_df['destination_name'] != 'EU27']
kor_imp_df = kor_imp_df[kor_imp_df['origin_name'] != 'EU27']
kor_exp_df = kor_exp_df[kor_exp_df['destination_name'] != 'EU27']

dict_industries = {"Agri_Food": [1, 24], "Mineral products": [25, 27], "Chemical": [28, 38],
                   "Plastic/Rubbers": [39, 40], "Raw Hide": [41, 43], "Wood Products": [44, 49],
                   "Textiles": [50, 63], "Footwears": [64, 71], "Base metal": [72, 83],
                   "Machinery/Elec. Equip": [84, 85], "Vehicle": [86, 89], "Optical/Photo. Instr.": [90, 92],
                   "Other": [93, 99], "Total": [101, 102]}

app.layout = html.Div([
    dcc.Dropdown(
        id="product-dropdown",
        options=[{"label": x, "value": x} 
                 for x in dict_industries.keys()],
        value = 'Total',
        placeholder="Select a product classification",
    ),
    html.Div(
    [
        html.P("Type the desired ranking (based on 2018 data)"),
        dbc.Input(id="styled-numeric-input", type="number", min=1, step=1, value = 3),
    ],
    ),
    dcc.Graph(id="line-chart"),
])

@app.callback(
    Output("line-chart", "figure"), 
    [Input("styled-numeric-input", "value"),
    Input("product-dropdown", "value")])
def update_line_chart(top, industry):
    fig = layout_share(mex_imp_df, mex_exp_df, kor_imp_df, kor_exp_df, industry, top)
    return fig

if __name__ == '__main__':
   app.run_server(debug=True)
