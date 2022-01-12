import dash
from dash.dependencies import Input, Output, State 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd 
import io 
import sqlalchemy 
import dash_bootstrap_components as dbc
import psycopg2
import plotly.offline as pyo
import plotly.figure_factory as ff
import numpy as np
from scipy import stats
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import geopandas as gpd
from google.cloud import secretmanager
from google.oauth2 import service_account
import os 
import pandas_gbq
from google.cloud import bigquery


current_directory = os.path.abspath(os.path.dirname(__file__))
path_to_service_account_json = os.path.join(current_directory, 'credentials/my-project-3604-337404-f179dd1d6873.json')

credentials = service_account.Credentials.from_service_account_file(path_to_service_account_json)
project_id = 'my-project-3604-337404'   
database = 'my-project-3604-337404.mercarie_data.mercarie_datatable' 


#initialize app 
external_stylesheets = ['https://bootswatch.com/5/journal/bootstrap.min.css']

app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=external_stylesheets)
server = app.server

# #initialize token for mapbox 
map_box_public_token = "pk.eyJ1IjoidG9ueXBhcmswMDEiLCJhIjoiY2t2dWVramFmODZqaDJucXBrbnhpZ2JreCJ9.-XXf1YI8YESgWbWODhZAZA"
px.set_mapbox_access_token(map_box_public_token)

#query for certain categories in category_1 then return df 
def query_category(*args):

    if args[1] == 'Pick your Second Category':
        query = f"""
    
        select * 
        from {database}
        where category_1 is not null 
        and category_1 = '{args[0]}'
        and category_2 is not null 
        and category_2 = category_2
        and category_3 is not null 
        and category_3 = category_3

        """
    elif args[2] == 'Pick your Third Category':
        query = f"""
    
        select * 
        from {database}
        where category_1 is not null 
        and category_1 = '{args[0]}'
        and category_2 is not null 
        and category_2 = '{args[1]}'
        and category_3 is not null 
        and category_3 = category_3

        """
    else: 
        query = f"""
    
        select * 
        from {database}
        where category_1 is not null 
        and category_1 = '{args[0]}'
        and category_2 is not null 
        and category_2 = '{args[1]}'
        and category_3 is not null 
        and category_3 = '{args[2]}'

        """


    
    df = pd.read_gbq(
        query,
        project_id=project_id,
        dialect='standard',
        credentials=credentials)
    
    return df

#query for all unique categories_1
category_options = pd.read_gbq(
    f"""
    select category_1 
    from 
        (select category_1, count(*) as count_cat
        from {database} 
        where category_1 is not null
        group by category_1 
        order by count_cat desc
        limit 100) as t
    where t.category_1 is not null 
    limit 13

    """, 
    project_id=project_id,
    dialect='standard',
    credentials=credentials)


##initialize second category list before updating
category_options_2 = pd.read_gbq(
    f"""
    select category_2 
    from 
        (select category_2, count(*) as count_cat
        from {database} 
        where category_2 is not null
        group by category_2 
        order by count_cat desc
        limit 100) as t
    where t.category_2 is not null 
    limit 13

    """, 
    project_id=project_id,
    dialect='standard',
    credentials=credentials)

##query unique categories in category_3 
category_options_3 = pd.read_gbq(
    f"""
    select category_3 
    from 
        (select category_3, count(*) as count_cat
        from {database} 
        where category_3 is not null
        group by category_3 
        order by count_cat desc
        limit 100) as t
    where t.category_3 is not null 
    limit 13

    """, 
    project_id=project_id,
    dialect='standard',
    credentials=credentials)


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

#ML inputs 
ml_inputs1 = dbc.Card(
    [
        dbc.CardBody([
        html.H5("Title"), 
        dbc.Input(
            id='title',
            type='text'

        ),
        html.Br(),
        html.H5("Category 1"),
        dcc.Dropdown(
            id = "Category_1",
            options = [
                {"label":x, "value":x} for x in category_options["category_1"]
            ], 
            value="Category_1" 
        ),  
        html.Br(),
        html.H5("Category 2"),
        dcc.Dropdown(
            id = "Category_2",
            options = [
                {"label":x, "value":x} for x in category_options_2["category_2"]
            ], 
            value="Category_2" 
        ), 
        html.Br(),
        html.H5("Category 3"),
        dcc.Dropdown(
            id = "Category_3",
            options = [
                {"label":x, "value":x} for x in category_options_3["category_3"]
            ], 
            value="Category_3" 
        ),
        html.Br(),
        html.H5("Shipping Price"), 
        dbc.Input(
            id='shipping_price',
            type='number'
        ),
        html.Br(),
        html.H5("Number of Images"), 
        dbc.Input(
            id='num_image',
            type='number'
        ),
        html.Br(),
        html.H5("Condition"), 
        dcc.Dropdown(
            id = "condition",
            options = [
                {"label":x, "value":x} for x in ['Poor', 'Fair', 'Good','Like New', 'New']
            ], 
            value="condition" 
        ), 
        html.Br(), 
        html.H5("Brand"), 
        dbc.Input(
            id='brand',
            type='text'
        ),
        html.Br(),
        # dcc.Dropdown(
        #     id = "Brand",
        #     options = [
        #         ##TO DO
        #     ]
        #     value="Brand" 
        # )     
            ])
            ]
)

ml_inputs2 = dbc.Card(
    [
        dbc.CardBody([
         html.H5("Location"), 
         # dcc.Dropdown(
        #     id = "Brand",
        #     options = [
        #         ##TO DO
        #     ]
        #     value="Brand" 
        # )
        dbc.Input(
            id='location',
            type='text'
        ),
        html.Br(),
        html.H5("Number of User Reviews"), 
        dbc.Input(
            id='Reviews',
            type='number'
        ),
        html.Br(),
        html.H5("Number of Listed Items"), 
        dbc.Input(
            id='Items',
            type='number'
        ),
        html.Br(),
        html.H5("Number of Sold Items"), 
        dbc.Input(
            id='Sold',
            type='number'
        ),
        html.Br(),
        html.H5("Profile Verified?"), 
        dcc.Dropdown(
            id = "Profile",
            options = [
                {"label":x, "value":x} for x in ['Yes','No']
            ], 
            value="Profile" 
        ),
        html.Br(),
        html.H5("Reliable?"), 
        dcc.Dropdown(
            id = "reliable",
            options = [
                {"label":x, "value":x} for x in ['Yes','No']
            ], 
            value="reliable" 
        ),
        html.Br(),
        html.H5("Fast Responder?"), 
        dcc.Dropdown(
            id = "response",
            options = [
                {"label":x, "value":x} for x in ['Yes','No']
            ], 
            value="response" 
        ),
        html.Br(),
        html.H5("Year Joined"), 
        dbc.Input(
            id='year_joined',
            type='number'
        ), 
        html.Br()
            ])
            ]
)

#app layout for Dash 
app.layout = html.Div([

dbc.Container(
    [
        dcc.Tabs(id="tabs", children = [
            dcc.Tab(label = "Explore Items", value="tab-1", children = [
                html.Br(),
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
                                id = "loading_graph", 
                                type = "default", 
                                children = [
                                     html.Br(),
                                    html.H1("Pricing Distribution"),
                                    html.Hr(), 
                                    dcc.Graph(id="distplot"),
                                    html.Br(),
                                    html.H1("Pricing Spread"),
                                    html.Hr(),
                                    dcc.Graph(id="boxplot")
                                    ]
                                    )
                                )
                        ]
                        ), 
                dbc.Row(
                        [
                        dbc.Col(
                            dcc.Loading(
                                id="loading_graph2",
                                type="default",
                                children=[ 
                                html.Br(),
                                html.H1("Top 10 Brands"),  
                                html.Hr(),
                                dcc.Graph(id="barchart"), 
                                html.Br(), 
                                html.H1("Geographic Distribution"),
                                html.Hr(),
                                dcc.Graph("geo_map")
                                ]
                                )
                            )
                        ]
                        )              
        

            ]), 
            dcc.Tab(label = "Price Items", value="tab-2", children=[
                html.Br(),
                html.H1("Under Construction..."),
                dbc.Row(
                        [
                        dbc.Col(ml_inputs1),
                        dbc.Col(ml_inputs2)
                        ], 
                    align = "center"
                ),
                dbc.Row(
                        [
                        dbc.Col(dbc.Card([
                            html.Br(), 
                            html.Div(
                                [dbc.Button("Calculate!",id="calculate_button", outline=True, color="primary", size="lg")],
                                className="d-grid gap-2 col-6 mx-auto"
                                ),
                            html.Br()
                    
        
                        ]))
                        ], 
                    align = "center"
                )

            ]), 

        ])
    ]

)
])


###callback functions

#update label for third dropdown based on previous two 
@app.callback(
    Output("third_dropdown", "options"),
    [
        Input("first_dropdown", "label"),
        Input("second_dropdown", "value") 
    ]
)
def change_third_dropdown(cat_1_label, cat_2_label):
    print(cat_1_label, cat_2_label)
    if cat_2_label == None or cat_1_label == None:
        raise PreventUpdate

    category_3_options = pd.read_gbq(
    f"""
    select category_3 
    from 
        (select category_3, count(*) as count_cat_3
        from {database} 
        where category_1 = '{cat_1_label}' and category_2 = '{cat_2_label}'
        group by category_3
        order by count_cat_3 desc) as t
    limit 10
    """, 
    project_id=project_id,
    dialect='standard',
    credentials=credentials)

    options = [
        {"label":x, "value":x} for x in category_3_options["category_3"]
        ]

    return options

#update label for second dropdown 
@app.callback(
    Output("second_dropdown", "options"),
    [Input("first_dropdown", "label")]
)
def change_second_dropdown(cat_1_label):

    if cat_1_label == None:
        raise PreventUpdate

    category_2_options = pd.read_gbq(
    f"""
    select category_2 
    from 
        (select category_2, count(*) as count_cat_2
        from {database} 
        where category_1 = '{cat_1_label}' 
        group by category_2
        order by count_cat_2 desc) as t
    limit 10
    """, 
    project_id=project_id,
    dialect='standard',
    credentials=credentials)

    options = [
        {"label":x, "value":x} for x in category_2_options["category_2"]
        ]

    return options

#callback for barchart for top 10 brands
@app.callback(
    Output("barchart", "figure"),
    [Input("search_button","n_clicks" ), 
    State(component_id="first_dropdown", component_property="label"), 
    State(component_id="second_dropdown", component_property="value"),
    State(component_id="third_dropdown", component_property="value")
    ]
)
def update_graph(button_click, category_label, second_label, third_label):
    print(category_label, second_label, third_label)
    if category_label == "Category":
        raise PreventUpdate
    cat_df = query_category(category_label, second_label, third_label)
    top_ten = cat_df["brand"].value_counts().reset_index(name="top_brands")[:10]

    fig = px.bar(
        top_ten, 
        x="index",
        y="top_brands"
    )
    # fig.add_vline(
    #     x = np.mean(cat_df.price), 
    #     line_dash ="dash", 
    #     line_color = "blue"
    # )
    return fig


#callback for geochart
@app.callback(
    Output("geo_map", "figure"),
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
    cat_df = cat_df["location"].value_counts().reset_index()

    usa = gpd.read_file("./states_21basic/states.shp")
    usa = usa[(usa["STATE_NAME"]!="Hawaii") & (usa["STATE_NAME"]!="Alaska") ]
    usa = usa.merge(cat_df, how="left", left_on="STATE_NAME", right_on="index")

    usa.rename(columns={"index":"State"}, inplace=True)
    usa.set_index("State", inplace=True)
    usa.rename(columns={"location":"Count"}, inplace=True)

    fig = px.choropleth_mapbox(
        usa, 
        geojson = usa.geometry, 
        locations = usa.index, 
        color = usa.Count, 
        zoom = 3.2, 
        center = {"lat":39, "lon":-95}, 
        color_continuous_scale=px.colors.sequential.Oranges,
        height = 900
    )

    return fig

#some change 

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
        x="price"
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
                    host = '0.0.0.0',
                    port = 8080
                    )


