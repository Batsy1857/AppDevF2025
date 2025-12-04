import pandas as pd
from plotly import express as px
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from dash import html, dcc, Input, Output


# Define allowed charts based on data type
CHART_OPTIONS = {
    'Categorical': ["Bar Chart", "Pie Chart"],
    'Numerical': ["Histogram", "Box Plot"],
    'All': ["Bar Chart", "Pie Chart", "Histogram", "Box Plot"]
}


fig = {}

layout = html.Div([
    html.H1("Univariate Analysis"),
    html.Br(),
    html.Br(),
    html.Label("Filter by Data Type:"),
    dcc.Dropdown(
        options=['All', 'Categorical', 'Numerical'],
        id='data_type_dropdown',
        value='All',  # Set default value to 'All'
        clearable=False
    ),
    html.Label("Select a variable:"),
    dcc.Dropdown(    
        options=[],
        id='col_dropdown',
        value=None,
        placeholder="Select a column..."
    ),
    html.Br(),
    html.Br(),

    dcc.Dropdown(
        options=[],
        id='chart_type_dropdown',
        value=None,
        placeholder="Select a chart type..."
    ),

    dcc.Graph(id='univariate_graph', figure=fig)
])


@app.callback(
    Output('col_dropdown', 'options'),
    Output('col_dropdown', 'value'),
    Input('data_type_dropdown', 'value'),
    Input("preprocessing-working-data", "data")
)
def update_column_options(selected_type, working_data):
    if not working_data:
        return [], None

    df = pd.DataFrame(working_data)

    numerical_cols = df.select_dtypes(include=['int64', 'Int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    all_cols = df.columns.tolist()

    # Default to 'All' if selected_type is None
    if selected_type == 'Numerical':
        filtered = numerical_cols
    elif selected_type == 'Categorical':
        filtered = categorical_cols
    else:  # 'All' or None
        filtered = all_cols

    options = [{'label': c, 'value': c} for c in filtered]
    
    # Reset column selection when filter changes
    return options, None


@app.callback(
    Output('chart_type_dropdown', 'options'),
    Output('chart_type_dropdown', 'value'),
    Input('col_dropdown', 'value'),
    Input("preprocessing-working-data", "data")
)
def update_chart_options(col_name, working_data):
    if not working_data or col_name is None:
        return [], None
    
    df = pd.DataFrame(working_data)

    numerical_cols = df.select_dtypes(include=['int64', 'Int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
    if col_name in numerical_cols:
        available_charts = CHART_OPTIONS['Numerical']
    elif col_name in categorical_cols:
        available_charts = CHART_OPTIONS['Categorical']
    else:
        available_charts = CHART_OPTIONS['All']
    
    return available_charts, None


@app.callback(
    Output('univariate_graph', 'figure'),
    Input('col_dropdown', 'value'),
    Input('chart_type_dropdown', 'value'),
    Input("preprocessing-working-data", "data")
)
def update_graph(col, chart_type, working_data):
    if not working_data or col is None or chart_type is None:
        return {}
    
    df = pd.DataFrame(working_data)

    if chart_type == 'Bar Chart':
        fig = px.bar(
            df[col].value_counts().reset_index(),
            x=col,
            y='count',
            height=600,
            width=900,
            color=col,
            text='count',
            title=f"Bar Chart Distribution of {col}"
        )
        fig.update_layout(title_x=0.5)
    
    elif chart_type == 'Box Plot':
        fig = px.box(
            df,
            x=col,
            height=600,
            width=800,
            color_discrete_sequence=['steelblue'],
            title=f"Box Plot of {col}"
        )
        fig.update_layout(title_x=0.5)

    elif chart_type == 'Histogram':
        fig = px.histogram(
            df,
            x=col,
            title=f"Histogram showing distribution of {col}"
        )
        fig.update_traces(
            marker_color='mediumseagreen',
            marker_line_color='black',
            marker_line_width=1.5
        )
        fig.update_layout(title_x=0.5)
    
    elif chart_type == 'Pie Chart':
        fig = px.pie(
            df[col].value_counts(),
            names=df[col].value_counts().index,
            values='count',
            height=600,
            width=900,
            title=f"Pie Chart of {col}"
        )
        fig.update_layout(title_x=0.5)

    return fig