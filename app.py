import dash 
import dash_core_components as dcc
import dash_html_components as html
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
#control
controls = dbc.Card(
    [
        dbc.CardBody([
        dbc.DropdownMenu(
            label="categories", 
            color="primary",
            size = "lg", 
            children=[
                dbc.DropdownMenuItem(item) for item in category_options["category_1"]
            ]
        )
        ],
        className="w-75 mb-3")

    ]

)



#app layout for Dash 
app.layout = dbc.Container(
[
    html.H1("Explore Items on Mercarie"), 
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(controls)
        ], 
        align = "center"
    )
], 
fluid=True
)



if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1')


