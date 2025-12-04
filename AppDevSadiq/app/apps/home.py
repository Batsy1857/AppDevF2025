from dash import dash
from dash import dcc, html, dash_table, callback, Input, Output, State
import pandas as pd
import base64
import io
from app import app


layout = html.Div([ 
    html.H3('Business Use Case'),
    html.P('This comprehensive data science application helps you analyze and preprocess your datasets effectively. It provides a complete pipeline for data exploration and preparation including:'),
    html.Ul([
        html.Li('Data Upload and Visualization'),
        html.Li('Univariate Analysis - Explore individual variables with various statistical visualizations'),
        html.Li('Bivariate Analysis - Understand relationships between two variables'),
        html.Li('Comprehensive Preprocessing Pipeline - Handle missing values, encode categorical variables, normalize data, and more'),
    ]),
    html.P('This tool is ideal for data scientists, analysts, and researchers who need to quickly explore and prepare data for machine learning models.'),
    html.Hr(),

    html.H3('Upload Your Dataset'),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Click to Upload CSV File'),
        multiple=False
    ),
    html.Div(id='upload-status'),
    html.Hr(),
    
    html.Div(id='output-container')
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return None, 'Please upload a CSV file.'
        return df, None
    except Exception as e:
        return None, f'Error: {str(e)}'
    
@callback(
    [Output('upload-status', 'children'),
     Output('output-container', 'children'),
     Output('stored-data', 'data')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)

def update_output(contents, filename):
    if contents is None:
        return 'No file uploaded', None, None

    df, error = parse_contents(contents, filename)

    if error:
        return error, None, None

    # Status message
    status = f'Uploaded: {filename} ({df.shape[0]} rows, {df.shape[1]} columns)'

    # Build info data
    info_data = []
    for col in df.columns:
        info_data.append({
            'Column': col,
            'Data Type': str(df[col].dtype),
            'Non-Null': df[col].notna().sum(),
            'Null': df[col].isna().sum(),
            'Null %': f"{(df[col].isna().sum() / len(df) * 100):.2f}%",
            'Unique': df[col].nunique()
        })

    info_df = pd.DataFrame(info_data)

    # Output preview and dataset info
    output = html.Div([
        html.H3('Data Preview (First 10 Rows)'),

html.Div(
    dash_table.DataTable(
        data=df.head(10).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_cell={'textAlign': 'center', 'padding': '8px'},
        page_size=10
    ),
    style={"display": "flex", "justifyContent": "center"}
),

        html.Hr(),

        html.H3('Dataset Information'),
        html.P(f'Total Rows: {df.shape[0]}'),
        html.P(f'Total Columns: {df.shape[1]}'),
        html.P(f'Total Missing Values: {df.isna().sum().sum()}'),
        html.P(f'Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB'),
        html.Hr(),

        html.H4('Column Details'),
        dash_table.DataTable(
            data=info_df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in info_df.columns],
            page_size=20,
            style_table={'width': '50%', 'margin': '20px 0'},
            style_cell={'textAlign': 'center', 'padding': '8px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': '#f1f1f1'}
        )
    ])

    # Return status, preview, and store the dataframe as JSON
    return status, output, df.to_dict('records')

