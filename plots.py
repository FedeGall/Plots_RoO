import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pathlib import Path

from plots_layout import *

input_path = Path('temp/kor_full.csv')

df = pd.read_csv(input_path, dtype = {'origin':'str', 'destination': 'str', 'product_code': 'str', 'chapters': 'str', 'industry': 'str'})
df['product_code'] = df['product_code'].apply(lambda x: '0' + x if len(x) == 1 else x)
df['product_code'] = df['product_code'].apply(lambda x: '0' + x if len(x) == 5 and re.match(r'[0-9]{5}', x) else x)

importers = set(df['destination_name'].unique())
exporters = set(df['origin_name'].unique())
countries = list(importers.union(exporters))
countries.sort()

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id="trade_partner",
        options=[{"label": x, "value": x} 
                 for x in countries],
        value=['EU28'],
        multi = True
    ),
    dbc.RadioItems(
        options=[
            {"label": "6-digit codes", "value": "6-digit codes"},
            {"label": "2-digit codes", "value": "2-digit codes"},
            {"label": "Industry", "value": "Industry"},
        ],
        value="Industry",
        inline = True,
        id="radioitems-input",
    ),
    dcc.Dropdown(
        id="product-dropdown",
        placeholder="Select a product classification",
        value = 'total',
    ),
    dbc.RadioItems(
        options=[
            {"label": "Log", "value": "Log"},
            {"label": "Growth rate", "value": "Growth rate"},
        ],
        value="Log",
        inline = True,
        id="radioitems-type",
    ),
    dcc.Graph(id="line-chart"),
])

@app.callback(
    Output('product-dropdown', 'options'),
    [Input("trade_partner", "value"),
    Input('radioitems-input', 'value')])
def update_product_dropdown(country, classification):
    if len(country) == 0:
        country.append('EU28')
    filtered_df = df[(df['origin_name'].isin(country)) | (df['destination_name'].isin(country))].copy()
    product_dict = product_choice(filtered_df)
    return [{'label': i, 'value': i} for i in product_dict[classification]]

@app.callback(
    Output("line-chart", "figure"), 
    [Input("trade_partner", "value"),
    Input("product-dropdown", "value"),
    Input("radioitems-type", "value")])
def update_line_chart(country, hs, plot_type):
    if len(country) == 0:
        country.append('EU28')
    filtered_df = df[(df['origin_name'].isin(country)) | (df['destination_name'].isin(country))].copy()
    filtered_df = filtered_df[filtered_df['product_code'] == hs]
    if len(country) == 1:
        fig = layout_single(filtered_df, plot_type)
        return fig
    elif len(country) > 1:
        fig = layout_multi(filtered_df, country, plot_type)
        return fig

app.run_server(debug=True)
