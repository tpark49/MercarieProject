import dash
from dash.dependencies import Input, Output, State 
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
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate


#initialize app 
app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

#initialize engine from postgresql
engine = create_engine(f"postgresql+psycopg2://{config.user_id}:{config.password}@localhost:5432/postgres", echo=False)

#query for certain categories in category_1 then return df 
def query_category(*args):
    category_1 = "category_1"
    category_2 = "category_2"
    category_3 = "category_3"

    if len(args)>0: 
        category_1 = args[0]
    if len(args)>1:
        category_2 = args[1]
    if len(args)>2:
        category_3 = args[2]

    df = pd.read_sql_query(
    "select * "\
    "from mercariedata1 "\
    "where category_1 is not null "\
    "and category_1 = '"+category_1+"' "\
    "and category_2 is not null "\
    "and category_2 = '"+category_2+"' "\
    "and category_3 is not null "\
    "and category_3 = '"+category_3+"';"
    ,engine) 

    return df

#query for all unique categories_1
category_options = pd.read_sql_query(
    "select category_1 from (select category_1, count(*) as count_cat "\
    "from mercariedata1 "\
    "group by category_1 "\
    "order by count_cat desc "\
    "limit 100) as t "\
    "where category_1 is not null "\
    "limit 13", engine)

# #query unique categories in category_2 
# category_options_2 = pd.read_sql_query(
#     "select category_2 from (select category_2, count(*) as count_cat "\
#     "from mercariedata1 "\
#     "group by category_2 "\
#     "order by count_cat desc "\
#     "limit 100) as t "\
#     "where category_2 is not null "\
#     "limit 13", engine)

# #query unique categories in category_2 
# category_options_3 = pd.read_sql_query(
#     "select category_3 from (select category_3, count(*) as count_cat "\
#     "from mercariedata1 "\
#     "group by category_2 "\
#     "order by count_cat desc "\
#     "limit 100) as t "\
#     "where category_2 is not null "\
#     "limit 13", engine)



#input list to query for dropdown
input_list = [item for item in category_options["category_1"]]


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
            label="Category", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item, id=f"dd_{item}") for item in category_options["category_1"]
            ]), 
        html.Br(),
        html.H5("Pick First Subcategory"),
        dbc.DropdownMenu(
            label="First Subcategory", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item) for item in category_options["category_1"]
            ]),
        html.Br(),  
        html.H5("Pick Second Subcategory"),
        dbc.DropdownMenu(
            label="Second Subcategory", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item) for item in category_options["category_1"]
            ]),
        html.Br(),
        html.Div(
            [dbc.Button("Search!",id="search_button", outline=True, color="primary", size="lg")],
            className="d-grid gap-2 col-6 mx-auto"
            )
            ])
            ]
)




#app layout for Dash 
app.layout = dbc.Container(
[
    html.H1("Explore Items on Mercarie"), 
    html.Br(),
    dbc.Row(
        [
            dbc.Col(first_card)
        ], 
        align = "center"
    ), 
    dbc.Row(
        [
 
            dbc.Col(

                dcc.Loading(
                    id="loading_graph",
                    type="default",
                    children=[
                        dcc.Graph(id="distplot")
                    ]
                )
                )
        ]
    ) 
], 
fluid=True
)

###callback functions
@app.callback(
    Output
)


@app.callback(
    Output("distplot", "figure"),
    [Input("search_button","n_clicks" ), 
    State(component_id="first_dropdown", component_property="label")
    ]
)
def update_graph(button_click, category_label):
    if category_label == "Category" or category_label == None:
        raise PreventUpdate
    cat_df = query_category(category_label)
    prices = [cat_df[np.abs(stats.zscore(cat_df["price"]))<2]["price"]]
    group_labels = ["distplot"]
    fig = ff.create_distplot(
        prices,
        group_labels,
        curve_type = "kde"
    )
    # fig.add_vline(
    #     x = np.mean(cat_df.price), 
    #     line_dash ="dash", 
    #     line_color = "blue"
    # )
    return fig

# @app.callback(
#     Output("loading_output", "children"), 
#     Input("distplot", "figure")
# )
# def input_triggers_spinner(value):
#     return value


#update graph based on dropdown selection
# @app.callback(
#     Output("distplot", "figure"), 
#     [
#         Input("first_dropdown", "label")
#     ]
# )
# def make_distribution(category_label):
#     if category_label == "Category":
#         raise PreventUpdate
#     print("Here")
#     cat_df = query_category(category_label)
#     print("here1")
#     prices = [cat_df[np.abs(stats.zscore(cat_df["price"]))<2]["price"]]
#     group_labels = ["distplot"]
#     fig = ff.create_distplot(
#         prices,
#         group_labels,
#         curve_type = "kde"
#     )
#     print("here2")
    # fig.add_vline(
    #     x = np.mean(cat_df.price), 
    #     line_dash ="dash", 
    #     line_color = "blue"
    # )
    #return fig
    
#update dropdown list to whichever is selected 
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


