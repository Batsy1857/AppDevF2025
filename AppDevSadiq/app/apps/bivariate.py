import pandas as pd
from plotly import express as px
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from dash import html,dcc,Input,Output

fig = {}

layout= html.Div([
    html.H1("Bivariate Analysis"),
    html.Br(),
    html.Br(),
    html.Label("Select your variables:"),
    html.Br(),
    html.Br(),
    html.Label("Select an x-axis variable"),
    dcc.Dropdown(
        options=[],
        id='x-axis_dropdown',
        value=None
        ),
    html.Br(),
    html.Br(),
    html.Label("Select a y-axis variable:"),
    dcc.Dropdown(    
        options=[],
        id='y-axis_dropdown',
        value=None
        ),
    html.Br(),
    html.Br(),
    html.Label("Select the type of analysis you want to perform:"),
    dcc.Dropdown(
        ["Scatter Plot","Box Plot","Clustered Bar Chart"],
        id='xy_chart_type_dropdown',
        value=None
    ),

    dcc.Graph(id='bivariate_graph',figure=fig)

])

@app.callback(
    Output('x-axis_dropdown', 'options'),
    Output('y-axis_dropdown', 'options'),
    Input("preprocessing-working-data", "data")
)
def populate_dropdowns(working_data):
    if not working_data:
        return [], []
    
    df = pd.DataFrame(working_data)
    options = [{'label': col, 'value': col} for col in df.columns]
    
    return options, options

@app.callback(
    Output('bivariate_graph','figure'),
    Input('x-axis_dropdown','value'),
    Input('y-axis_dropdown','value'),
    Input('xy_chart_type_dropdown','value'),
    Input("preprocessing-working-data", "data")
     
)

def update_bivariate_graph(x,y,chart_type,working_data):
    df = pd.DataFrame(working_data)

    
    if chart_type == "Box Plot":
        fig = px.box(
        df,
        x=x,
        y=y,
        color=y,
        height=600,
        width=800,
        title=f"Boxplot Distribution of our class variable {y} against {x}")

        fig.update_layout(title_x = 0.5)

    elif chart_type == "Scatter Plot":
        fig = px.scatter(
                df,
                x=x,
                y=y,
                color=y,
                title=f"Scatter Plot of {y} against {x}")
        
        fig.update_layout(title_x = 0.5)

    elif chart_type == "Clustered Bar Chart":
        freq = df.groupby([x, y]).size().reset_index(name="Count")
        fig = px.bar(
            freq,
            x=x,
            y="Count",
            color=y,
            title=f"Clustered Bar Chart comparing distribution of {y} against {x}", 
            barmode="group")
        fig.update_layout(title_x = 0.5)

    return fig
