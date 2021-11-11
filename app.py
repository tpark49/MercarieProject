import dash
from dash.dependencies import Input, Output 
import dash_core_components as dcc
import dash_html_components as html
from flask.scaffold import F
import plotly.express as px
import pandas as pd 
import io 
from sqlalchemy import create_engine, event
import dash_bootstrap_components as dbc
import psycopg2
import config
import plotly.offline as pyo
import plotly.figure_factory as ff
import numpy as np
from scipy import stats


#initialize app 
app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

#initialize engine from postgresql
engine = create_engine(f"postgresql+psycopg2://{config.user_id}:{config.password}@localhost:5432/postgres", echo=False)

#query unique categories in category_1 
category_options = pd.read_sql_query(
    "select category_1 from (select category_1, count(*) as count_cat "\
    "from mercariedata1 "\
    "group by category_1 "\
    "order by count_cat desc "\
    "limit 100) as t "\
    "where category_1 is not null "\
    "limit 13", engine)

#query unique categories in category_2 
# category_options_2 = pd.read_sql_query(
#     "select category_2 from (select category_2, count(*) as count_cat "\
#     "from mercariedata1 "\
#     "group by category_2 "\
#     "order by count_cat desc "\
#     "limit 100) as t "\
#     "where category_2 is not null "\
#     "limit 13", engine)


#create dictionary for category_1
category_dictionary = {}
for item in category_options["category_1"]:
    category_dictionary[f"dd_{item}"] = item


#list of cards 
first_card = dbc.Card(
    [
        dbc.CardBody([
        html.H5("Pick a Broad Category of Your Choice"),
        dbc.DropdownMenu(
            id = "first_dropdown",
            label="Categories", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item, id=f"dd_{item}") for item in category_options["category_1"]
            ]), 
        html.Br(),
        html.H5("Pick First Subcategory"),
        dbc.DropdownMenu(
            label="1st Subcategory", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item) for item in category_options["category_1"]
            ])
            ])
            ]
)




#app layout for Dash 
app.layout = dbc.Container(
[
    html.H1("Explore Items on Mercarie"), 
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(first_card)
        ], 
        align = "center"
    ), 
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="displot"))
        ]

    )
], 
fluid=True
)


#callback functions

#update graph based on 
@app.callback(
    Output("displot", "figure"), 
    [
        Input()
    ]
)




#update dropdown list to whichever is selected 
input_list = [item for item in category_options["category_1"]]
@app.callback(
    Output("first_dropdown", "label"), 
    [Input(f"dd_{item}", "n_clicks") for item in category_options["category_1"]]
)
def update_label(*input_list):
    ctx = dash.callback_context

    # if (n1 is None and n2 is None) or not ctx.triggered:
    #     return "Not Selected"
    if all(item is None for item in input_list) or not ctx.triggered: 
        return "Category"
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return category_dictionary[button_id]

if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1')


