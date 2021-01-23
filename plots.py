import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import re
from pathlib import Path

input_path = Path('temp/kor_full.csv')

df = pd.read_csv(input_path, dtype = {'origin':'str', 'destination': 'str', 'product_code': 'str', 'chapters': 'str', 'industry': 'str'})
df['product_code'] = df['product_code'].apply(lambda x: '0' + x if len(x) == 1 else x)
df['product_code'] = df['product_code'].apply(lambda x: '0' + x if len(x) == 5 and re.match(r'[0-9]{5}', x) else x)

importers = set(df['destination_name'].unique())
exporters = set(df['origin_name'].unique())
countries = list(importers.union(exporters))
countries.sort()

def product_choice(df):
    products = list(set(df['product_code'].unique()))
    hs_codes = []
    hs_chapters = []
    industry = []
    for code in products:
        if len(code) == 6 and re.match(r'[0-9]{6}', code):
            hs_codes.append(code)
        elif len(code) == 5 and re.match(r'[0-9]{5}', code):
            hs_codes.append('0' + code)
        elif len(code) == 1 and re.match(r'[0-9]{1,}', code):
            hs_chapters.append('0' + code)
        elif len(code) == 2 and re.match(r'[0-9]{2,}', code):
            hs_chapters.append(code)
        else:
            industry.append(code)
    hs_codes.sort()
    hs_chapters.sort()
    industry.sort()
    product_dict = {"6-digit codes": hs_codes, "2-digit codes": hs_chapters, "Industry": industry}
    return product_dict

def layout_single(df, plot_type):
    import_df = df[df['trade_flow'] == "Import"].copy()
    export_df = df[df['trade_flow'] == "Export"].copy()
    fig = go.Figure()
    x_imp = import_df["year"]
    x_exp = export_df["year"]
    if plot_type == "Log":
        y_imp = import_df["value_log"]
        y_exp = export_df["value_log"]
        text_imp = [f"Year: {import_df.iloc[indice]['year']} <br>Imports: {import_df.iloc[indice]['value']:,.2f} <br>Imports (log): {import_df.iloc[indice]['value_log']:,.2f}" for indice in range(len(import_df))]
        text_exp = [f"Year: {export_df.iloc[indice]['year']} <br>Exports: {export_df.iloc[indice]['value']:,.2f} <br>Exports (log): {np.log(export_df.iloc[indice]['value']):,.2f}" for indice in range(len(export_df))]
    elif plot_type == "Growth rate":
        y_imp = import_df["value_growth"]
        y_exp = export_df["value_growth"]
        text_imp = [f"Year: {import_df.iloc[indice]['year']} <br>Imports change: {import_df.iloc[indice]['value_change']:,.2f} <br>Imports (log change): {import_df.iloc[indice]['value_growth']:.2%}" for indice in range(len(import_df))]
        text_exp = [f"Year: {export_df.iloc[indice]['year']} <br>Exports change: {export_df.iloc[indice]['value_change']:,.2f} <br>Exports (log change): {export_df.iloc[indice]['value_growth']:.2%}" for indice in range(len(export_df))]
    fig.add_trace(go.Scatter(x = x_imp, y = y_imp, mode = 'lines+markers', name = 'Imports',
                            hoverinfo = "text", hovertext = text_imp))
    fig.add_trace(go.Scatter(x = x_exp, y = y_exp, mode = 'lines+markers', name = 'Exports',
                            hoverinfo = "text", hovertext = text_exp))
    fig.update_layout(plot_bgcolor = 'white', paper_bgcolor = 'white')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_xaxes(tickformat = 'Y')
    if plot_type == "Growth rate":
        fig.update_yaxes(tickformat = '%')
    fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
    return fig

def layout_multi(df, country_list, plot_type):
    import_df = df[df['trade_flow'] == "Import"].copy()
    export_df = df[df['trade_flow'] == "Export"].copy()
    fig = make_subplots(rows=2, cols=1, subplot_titles = ("Imports", "Exports"), shared_xaxes = True, vertical_spacing = 0.2)
    for country in country_list:
        red_imp_df = import_df[import_df['origin_name'] == country].copy()
        red_exp_df = export_df[export_df['destination_name'] == country].copy()
        x_imp = red_imp_df["year"]
        x_exp = red_exp_df["year"]
        if plot_type == "Log":
            y_imp = red_imp_df["value_log"]
            y_exp = red_exp_df["value_log"]
            text_imp = [f"Year: {red_imp_df.iloc[indice]['year']} <br>Country: {country} <br>Imports: {red_imp_df.iloc[indice]['value']:,.2f} <br>Imports (log): {red_imp_df.iloc[indice]['value_log']:,.2f}" for indice in range(len(red_imp_df))]
            text_exp = [f"Year: {red_exp_df.iloc[indice]['year']} <br>Country: {country} <br>Exports: {red_exp_df.iloc[indice]['value']:,.2f} <br>Exports (log): {red_exp_df.iloc[indice]['value_log']:,.2f}" for indice in range(len(red_exp_df))]
        elif plot_type == "Growth rate":
            y_imp = red_imp_df["value_growth"]
            y_exp = red_exp_df["value_growth"]
            text_imp = [f"Year: {red_imp_df.iloc[indice]['year']} <br>Country: {country} <br>Imports change: {red_imp_df.iloc[indice]['value_change']:,.2f} <br>Imports (log change): {red_imp_df.iloc[indice]['value_growth']:.2%}" for indice in range(len(red_imp_df))]
            text_exp = [f"Year: {red_exp_df.iloc[indice]['year']} <br>Country: {country} <br>Exports change: {red_exp_df.iloc[indice]['value_change']:,.2f} <br>Exports (log change): {red_exp_df.iloc[indice]['value_growth']:.2%}" for indice in range(len(red_exp_df))]
        fig.add_trace(go.Scatter(x = x_imp, y = y_imp, mode = 'lines+markers', name = f"{country} - Imports",
                                hoverinfo = "text", hovertext = text_imp),
                       row = 1, col = 1)
        fig.add_trace(go.Scatter(x = x_exp, y = y_exp, mode = 'lines+markers', name = f"{country} - Exports",
                                hoverinfo = "text", hovertext = text_exp),
                       row = 2, col = 1)
    fig.update_layout(plot_bgcolor = 'white', paper_bgcolor = 'white')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_xaxes(tickformat = 'Y')
    if plot_type == "Growth rate":
        fig.update_yaxes(tickformat = '%')
    fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
    return fig

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
