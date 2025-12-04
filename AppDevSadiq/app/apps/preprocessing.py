import pandas as pd
from dash import html, dcc, dash_table, Input, Output, State, callback_context, no_update
from app import app

layout = html.Div([

    html.H2("Data Preprocessing Page to help clean your data"),
    html.Br(),
    
    html.Div([
        html.Button("Reset to Original Data", id="reset-preprocessing-btn", n_clicks=0, 
                   style={"margin-right": "10px"}),
        html.Span(id="preprocessing-status", style={"font-style": "italic", "color": "#666"})
    ]),
    html.Br(),

    dcc.Tabs([
        # ----------------------
        # Tab 1: Missing Values
        # ----------------------
        dcc.Tab(label='Treat Null/Missing Values', children=[
            html.H3("Missing Values Overview"),
            html.Hr(),

            dash_table.DataTable(
                id="missing-values-table",
                style_table={'width': '50%', 'margin': '20px 0'},
                style_cell={'textAlign': 'center', 'padding': '8px'},
                style_header={'fontWeight': 'bold', 'backgroundColor': '#f1f1f1'}
            ),

            html.Br(),
            html.Label("Select a column"),
            dcc.Dropdown(id="missing_col_dropdown", placeholder="Choose a column", style={"width": "50%"}),
            html.Br(),

            html.Label("Select treatment method"),
            dcc.Dropdown(
                id="treating_miss_val-dropdown",
                placeholder="Select method",
                options=[
                    {"label": "Drop Missing Values in Selected Column", "value": "drop"},
                    {"label": "Replace with Mean", "value": "mean"},
                    {"label": "Replace with Median", "value": "median"},
                    {"label": "Replace with Mode", "value": "mode"}
                ],
                style={"width": "50%"}
            ),
            html.Br(),
            html.Button("Apply Missing Value Treatment", id="apply-missing-btn", n_clicks=0),
            html.Br(), html.Br(),
            html.Div(id='output-missingvalues', style={"font-weight": "bold", "color": "#2a2a2a"})
        ],             
        
   ),

        # ----------------------
        # Tab 2: Change Dtypes
        # ----------------------
        dcc.Tab(label='Change Data Types of Column(s)', children=[
            html.H3("Change Column Data Types"),
            html.Br(),

            # ======= NEW DTYPE TABLE =======
            dash_table.DataTable(
                id="dtype-table",
                style_table={'width': '50%', 'margin': '20px 0'},
                style_cell={'textAlign': 'center', 'padding': '8px'},
                style_header={'fontWeight': 'bold', 'backgroundColor': '#f1f1f1'}
            ),
            html.Br(),

            html.Label("Select a column"),
            dcc.Dropdown(id="dtype-column", placeholder="Choose a column", style={"width": "50%"}),
            html.Br(),

            html.Label("Select new data type"),
            dcc.Dropdown(
                id="dtype-target",
                placeholder="Convert column to...",
                options=[
                    {"label": "Integer", "value": "int"},
                    {"label": "Float", "value": "float"},
                    {"label": "String", "value": "str"},
                    {"label": "Category", "value": "category"},
                    {"label": "Datetime", "value": "datetime"}
                ],
                style={"width": "50%"}
            ),
            html.Br(),

            html.Button("Apply Conversion", id="apply-dtype-btn", n_clicks=0),
            html.Br(), html.Br(),
            html.Div(id="dtype-output", style={"font-weight": "bold", "color": "#2a2a2a"})
        ]),
        
    ]),

    html.Br(),
    html.Button("Download Clean CSV", id="download-btn", n_clicks=0),
    dcc.Download(id="download-clean-csv")
])


# --------------------------------------------
# STEP 1: Initialize working data
# --------------------------------------------
@app.callback(
    Output("preprocessing-working-data", "data"),
    Output("preprocessing-modified-flag", "data"),
    Output("preprocessing-status", "children"),
    Input("stored-data", "data"),
    Input("reset-preprocessing-btn", "n_clicks"),
    State("stored-data", "data"),
    prevent_initial_call=False
)
def initialize_working_data(stored_data_trigger, reset_clicks, stored_data_state):
    ctx = callback_context
    
    if not stored_data_state:
        return None, False, ""
    
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == "reset-preprocessing-btn":
            return stored_data_state, False, "✓ Reset to original data"
    
    return stored_data_state, False, ""


# --------------------------------------------
# STEP 2: Populate dropdowns
# --------------------------------------------
@app.callback(
    Output("dtype-column", "options"),
    Output("missing_col_dropdown", "options"),
    Input("preprocessing-working-data", "data")
)
def populate_columns(working_data):
    if not working_data:
        return [], []
    df = pd.DataFrame(working_data)
    options = [{"label": col, "value": col} for col in df.columns]
    return options, options


# --------------------------------------------
# STEP 3: Missing values table
# --------------------------------------------
@app.callback(
    Output("missing-values-table", "columns"),
    Output("missing-values-table", "data"),
    Input("preprocessing-working-data", "data")
)
def update_missing_table(working_data):
    if not working_data:
        return [], []
    df = pd.DataFrame(working_data)
    missing_df = df.isnull().sum().reset_index()
    missing_df.columns = ["Column", "Missing Values"]
    return (
        [{"name": col, "id": col} for col in missing_df.columns],
        missing_df.to_dict("records")
    )


# --------------------------------------------
# NEW: Dtype table
# --------------------------------------------
@app.callback(
    Output("dtype-table", "columns"),
    Output("dtype-table", "data"),
    Input("preprocessing-working-data", "data")
)
def update_dtype_table(working_data):
    if not working_data:
        return [], []

    df = pd.DataFrame(working_data)
    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str)
    })

    return (
        [{"name": col, "id": col} for col in dtype_df.columns],
        dtype_df.to_dict("records")
    )


# --------------------------------------------
# STEP 4: Dtype conversion (unchanged)
# --------------------------------------------
@app.callback(
    Output("preprocessing-working-data", "data", allow_duplicate=True),
    Output("preprocessing-modified-flag", "data", allow_duplicate=True),
    Output("dtype-output", "children"),
    Input("apply-dtype-btn", "n_clicks"),
    State("dtype-column", "value"),
    State("dtype-target", "value"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def handle_dtype_conversion(n_clicks, dtype_col, dtype_target, working_data):
    if not working_data or not dtype_col or not dtype_target:
        return no_update, no_update, ""

    df = pd.DataFrame(working_data)
    col_data = df[dtype_col]

    try:
        # ===============================
        # VALIDATION CHECKS BEFORE APPLYING
        # ===============================

        if dtype_target == "int":
            # Check if ALL non-null values are numeric
            if not pd.to_numeric(col_data.dropna(), errors='coerce').notnull().all():
                return no_update, no_update, f"Error: Column '{dtype_col}' contains non-numeric values and cannot be converted to integer."
            
            numeric_col = pd.to_numeric(col_data, errors='coerce')
            df[dtype_col] = numeric_col.round().astype("Int64")

        elif dtype_target == "float":
            if not pd.to_numeric(col_data.dropna(), errors='coerce').notnull().all():
                return no_update, no_update, f"Error: Column '{dtype_col}' contains non-numeric values and cannot be converted to float."

            df[dtype_col] = pd.to_numeric(col_data, errors='coerce')

        elif dtype_target == "str":
            df[dtype_col] = col_data.astype(str)

        elif dtype_target == "category":
            df[dtype_col] = col_data.astype("category")

        elif dtype_target == "datetime":
            # Validate that datetime conversion is possible
            test_conversion = pd.to_datetime(col_data, errors='coerce')
            if test_conversion.isnull().all() and col_data.notnull().any():
                return no_update, no_update, f"Error: Column '{dtype_col}' cannot be converted into datetime format."

            df[dtype_col] = test_conversion

        # ===============================
        msg = f"✓ Column '{dtype_col}' converted to {dtype_target}."
        return df.to_dict("records"), True, msg

    except Exception:
        return no_update, no_update, f"Error converting '{dtype_col}' to {dtype_target}'."

# --------------------------------------------
# STEP 5: Missing values handler
# --------------------------------------------
@app.callback(
    Output("preprocessing-working-data", "data", allow_duplicate=True),
    Output("preprocessing-modified-flag", "data", allow_duplicate=True),
    Output("output-missingvalues", "children"),
    Input("apply-missing-btn", "n_clicks"),
    State("missing_col_dropdown", "value"),
    State("treating_miss_val-dropdown", "value"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def handle_missing_values(n_clicks, miss_col, miss_method, working_data):
    if not working_data or not miss_col or not miss_method:
        return no_update, no_update, ""
    
    df = pd.DataFrame(working_data)
    
    try:
        if miss_method == "drop":
            before = df.shape[0]
            df.dropna(subset=[miss_col], inplace=True)
            after = df.shape[0]
            msg = f"Dropped {before - after} rows from '{miss_col}'."
            
        elif miss_method == "mean":
            df[miss_col].fillna(df[miss_col].mean(), inplace=True)
            msg = f"Filled missing values in '{miss_col}' with mean."
            
        elif miss_method == "median":
            df[miss_col].fillna(df[miss_col].median(), inplace=True)
            msg = f"Filled missing values in '{miss_col}' with median."
            
        elif miss_method == "mode":
            mode_val = df[miss_col].mode()
            if len(mode_val) > 0:
                df[miss_col].fillna(mode_val[0], inplace=True)
                msg = f"Filled missing values in '{miss_col}' with mode."
            else:
                return no_update, no_update, f"No mode found for '{miss_col}'."
        
        return df.to_dict('records'), True, msg
        
    except Exception:
        return no_update, no_update, "Error handling missing values"


# --------------------------------------------
# STEP 6: Status indicator
# --------------------------------------------
@app.callback(
    Output("preprocessing-status", "children", allow_duplicate=True),
    Input("preprocessing-modified-flag", "data"),
    prevent_initial_call=True
)
def update_status_indicator(is_modified):
    if is_modified:
        return "Data has been modified (unsaved changes)"
    return ""


# --------------------------------------------
# STEP 7: Download
# --------------------------------------------
@app.callback(
    Output("download-clean-csv", "data"),
    Input("download-btn", "n_clicks"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def download_clean_csv(n_clicks, working_data):
    if not working_data:
        return no_update
    df = pd.DataFrame(working_data)
    return dcc.send_data_frame(df.to_csv, "cleaned_data.csv", index=False)
