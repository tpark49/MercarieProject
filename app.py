import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd 
import io 
import boto3

#initialize app 
app = dash.Dash(__name__)


#import df 
# client = boto3.client("s3")
# obj = client.get_object(Bucket = "mercariebucket", Key="total_data.csv")
# df = pd.read_csv(io.BytesIO(obj["Body"].read()))

df  = pd.read_csv("~/Desktop/data/data3.csv")

fig = px.line(df["shipping_price"])


app.layout = html.Div(children=[
    html.H1(children="Hello Dash V2"),

    dcc.Graph(figure = fig)
]
)



if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1')


