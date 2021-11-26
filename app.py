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
    print(args)

    if len(args)==1: 
        category_1 = args[0]
        category_1_query = "and category_1 = '"+category_1+"' "
        category_2_query = "and category_2 = category_2 "
        category_3_query = "and category_3 = category_3 "
    elif len(args) ==2:
        category_1 = args[0]
        category_2 = args[1]
        category_1_query = "and category_1 = '"+category_1+"' "
        category_2_query = "and category_2 = '"+category_2+"' "
        category_3_query = "and category_3 = category_3 "
    elif len(args) ==3: 
        category_1 = args[0]
        category_2 = args[1]
        category_3 = args[2]
        category_1_query = "and category_1 = '"+category_1+"' "
        category_2_query = "and category_2 = '"+category_2+"' "
        category_3_query = "and category_3 = '"+category_3+"' "

    df = pd.read_sql_query(
    "select * "\
    "from mercariedata1 "\
    "where category_1 is not null "\
    +category_1_query+
    "and category_2 is not null "\
    +category_2_query+
    "and category_3 is not null "\
    +category_3_query
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

##initialize second category list before updating
category_options_2 = pd.read_sql_query(
    "select category_2 from (select category_2, count(*) as count_cat "\
    "from mercariedata1 where category_2 is not null "\
    "group by category_2 "\
    "order by count_cat desc) as t "\
    "limit 10", engine)

##query unique categories in category_3 
category_options_3 = pd.read_sql_query(
    "select category_3 from (select category_3, count(*) as count_cat "\
    "from mercariedata1 "\
    "group by category_3 "\
    "order by count_cat desc "\
    "limit 100) as t "\
    "where category_3 is not null "\
    "limit 13", engine)


#create dictionary for category_1
category_dictionary = {}
for item in category_options["category_1"]:
    category_dictionary[f"dd_{item}"] = item

# #create dictionary for category_2
# global_category_2_dict = {}
# for item in category_options_2["category_2"]:
#     global_category_2_dict[f"dd_2_{item}"] = item


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
        html.H5("First Subcategory"), 
        dcc.Dropdown(
            id = "second_dropdown",
            options = [
                {"label":x, "value":x} for x in category_options_2["category_2"]
            ], 
            value="Pick your Second Category" 
        ),
        html.Br(),
        html.H5("Second Subcategory"), 
        dcc.Dropdown(
            id = "third_dropdown",
            options = [
                {"label":x, "value":x} for x in category_options_3["category_3"]
            ], 
            value="Pick your Third Category" 
        ),
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
                        dcc.Graph(id="distplot"),
                        dcc.Graph(id="boxplot")
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
    Output("third_dropdown", "options"),
    [
        Input("first_dropdown", "label"),
        Input("second_dropdown", "value") 
    ]
)
def change_third_dropdown(cat_1_label, cat_2_label):
    if cat_2_label == None or cat_1_label == None:
        raise PreventUpdate

    category_3_options = pd.read_sql_query(
        "select category_3 from "\
        "(select category_3, count(*) as count_cat_3 "\
        "from mercariedata1 "\
        "where category_1 = '" +cat_1_label+"' and category_2= '" + cat_2_label + "' "\
        "group by category_3 "\
        "order by count_cat_3 desc) as t "\
        "limit 10", engine)

    options = [
        {"label":x, "value":x} for x in category_3_options["category_3"]
        ]

    return options


@app.callback(
    Output("second_dropdown", "options"),
    [Input("first_dropdown", "label")]
)
def change_second_dropdown(cat_1_label):

    if cat_1_label == None:
        raise PreventUpdate
    category_2_options = pd.read_sql_query(
        "select category_2 from "\
        "(select category_2, count(*) as count_cat_2 "\
        "from mercariedata1 "\
        "where category_1 = '" +cat_1_label+"' "\
        "group by category_2 "\
        "order by count_cat_2 desc) as t "\
        "limit 10", engine)

    options = [
        {"label":x, "value":x} for x in category_2_options["category_2"]
        ]

    return options


#callback for distplot
@app.callback(
    Output("distplot", "figure"),
    [Input("search_button","n_clicks" ), 
    State(component_id="first_dropdown", component_property="label"), 
    State(component_id="second_dropdown", component_property="value"),
    State(component_id="third_dropdown", component_property="value")
    ]
)
def update_graph(button_click, category_label, second_label, third_label):
    if category_label == "Category":
        raise PreventUpdate
    cat_df = query_category(category_label, second_label, third_label)

    prices = [cat_df[np.abs(stats.zscore(cat_df["price"]))<1.65]["price"]]
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


#callback for boxplot
@app.callback(
    Output("boxplot", "figure"),
    [Input("search_button","n_clicks" ), 
    State(component_id="first_dropdown", component_property="label"), 
    State(component_id="second_dropdown", component_property="value"),
    State(component_id="third_dropdown", component_property="value")
    ]
)
def update_graph(button_click, category_label, second_label, third_label):
    if category_label == "Category":
        raise PreventUpdate
    cat_df = query_category(category_label, second_label, third_label)

    prices = [cat_df[np.abs(stats.zscore(cat_df["price"]))<1.65]["price"]]
    group_labels = ["distplot"]
    fig = px.box(
        cat_df,
        x="price", 
        title = "Pricing Distribution"
    )
    # fig.add_vline(
    #     x = np.mean(cat_df.price), 
    #     line_dash ="dash", 
    #     line_color = "blue"
    # )
    return fig

    
#update dropdown list to whichever is selected for category_1
@app.callback(
    Output("first_dropdown", "label"), 
    [Input(f"dd_{item}", "n_clicks") for item in category_options["category_1"]] 
)
def update_label(*input_list):
    ctx = dash.callback_context

    if all(item is None for item in input_list) or not ctx.triggered: 
        return "Category"
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    return category_dictionary[button_id]


if __name__ == '__main__':
    app.run_server(debug=True,
                    host = '127.0.0.1',
                    port = 8051
                    )


