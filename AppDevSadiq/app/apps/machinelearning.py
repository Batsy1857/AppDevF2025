import pandas as pd
from dash import html, dcc, Input, Output, State, no_update
from app import app
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

layout = html.Div([
    html.H2("Select from the options below"),

    dcc.Tabs([

        # ------------------------
        # Normalization Tab
        # ------------------------
        dcc.Tab(label="Normalization (Z-Score)", children=[
            html.Br(),
            html.Button("Apply Z-Score Normalization to all Numeric Columns", id="btn-normalize"),
            html.Div(id="normalize-msg"),
            html.Br(),
            html.Button("Download Normalized CSV", id="download-normalized-btn"),
            dcc.Download(id="download-normalized-data")
        ]),

        # ------------------------
        # Discretization Tab (Equal Width)
        # ------------------------
        dcc.Tab(label="Discretization (Equal Width)", children=[
            html.Br(),
            html.Label("Select Column to Discretize"),
            dcc.Dropdown(id="disc-col"),
            html.Br(),
            html.Label("Number of Bins:"),
            dcc.Input(id="num-bins", type="number", value=4, min=2, max=10),
            html.Br(),
            html.Br(),
            html.Button("Apply Equal-Width Discretization", id="btn-discretize"),
            html.Div(id="discretize-msg"),
            html.Br(),
            html.Button("Download Discretized CSV", id="download-discretized-btn"),
            dcc.Download(id="download-discretized-data")
        ]),

        # ------------------------
        # Encoding Tab
        # ------------------------
        dcc.Tab(label="Encoding", children=[
            html.Br(),
            html.Label("Select Class Variable (target):"),
            dcc.Dropdown(id="class-var-dropdown"),
            html.Br(),
            html.Button("Apply One-Hot Encoding", id="btn-encode"),
            html.Div(id="encode-msg"),
            html.Br(),
            html.Button("Download Encoded CSV", id="download-encoded-btn"),
            dcc.Download(id="download-encoded-data")
        ]),

        # ------------------------
        # Train/Test Split Tab
        # ------------------------
        dcc.Tab(label="Train/Test Split", children=[
            html.Br(),
            html.Label("Test Size (0-1):"),
            dcc.Input(id="test-size", type="number", value=0.3, min=0.1, max=0.5, step=0.05),
            html.Br(),
            html.Br(),
            html.Button("Perform Train/Test Split", id="btn-split"),
            html.Div(id="split-msg"),
            html.Br(),
            html.Div([
                html.Button("Download Train Data", id="download-train-btn", style={"marginRight": "10px"}),
                html.Button("Download Test Data", id="download-test-btn")
            ]),
            dcc.Download(id="download-train-data"),
            dcc.Download(id="download-test-data")
        ])
    ]),
    
    # Store split data
    dcc.Store(id="train-data-store"),
    dcc.Store(id="test-data-store")
])

# ------------------------
# Normalization
# ------------------------
@app.callback(
    Output("normalize-msg", "children"),
    Output("preprocessing-working-data", "data", allow_duplicate=True),
    Input("btn-normalize", "n_clicks"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def normalize_data(n_clicks, data):
    if not n_clicks or data is None:
        return "", no_update
    df = pd.DataFrame(data)
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) == 0:
        return "No numeric columns to normalize.", no_update
    df[num_cols] = (df[num_cols] - df[num_cols].mean()) / df[num_cols].std()
    return "Z-Score normalization applied.", df.to_dict('records')

@app.callback(
    Output("download-normalized-data", "data"),
    Input("download-normalized-btn", "n_clicks"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def download_normalized(n_clicks, data):
    if not n_clicks or data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "normalized_data.csv", index=False)

# ------------------------
# Discretization (Equal Width)
# ------------------------
@app.callback(
    Output("disc-col", "options"),
    Input("preprocessing-working-data", "data")
)
def populate_disc_columns(data):
    if not data:
        return []
    df = pd.DataFrame(data)
    return [{"label": col, "value": col} for col in df.select_dtypes(include="number")]

@app.callback(
    Output("discretize-msg", "children"),
    Output("preprocessing-working-data", "data", allow_duplicate=True),
    Input("btn-discretize", "n_clicks"),
    State("disc-col", "value"),
    State("num-bins", "value"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def discretize_column(n_clicks, col, num_bins, data):
    if not n_clicks or not data or not col:
        return "", no_update
    
    df = pd.DataFrame(data)
    
    # Use pd.cut for equal-width discretization
    try:
        labels = list(range(num_bins))
        df[col] = pd.cut(df[col], bins=num_bins, labels=labels, duplicates="drop")
        df[col] = df[col].astype(str)  # Convert Interval to string
        return f"Column '{col}' discretized into {num_bins} equal-width bins.", df.to_dict('records')
    except Exception as e:
        return f"Error discretizing column: {str(e)}", no_update

@app.callback(
    Output("download-discretized-data", "data"),
    Input("download-discretized-btn", "n_clicks"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def download_discretized(n_clicks, data):
    if not n_clicks or data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "discretized_data.csv", index=False)

# ------------------------
# Encoding
# ------------------------
@app.callback(
    Output("class-var-dropdown", "options"),
    Input("preprocessing-working-data", "data")
)
def load_class_variable_options(data):
    if not data:
        return []
    df = pd.DataFrame(data)
    cat_cols = df.select_dtypes(include="object").columns
    return [{"label": col, "value": col} for col in cat_cols]

@app.callback(
    Output("encode-msg", "children"),
    Output("preprocessing-working-data", "data", allow_duplicate=True),
    Input("btn-encode", "n_clicks"),
    State("class-var-dropdown", "value"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def encode_data(n_clicks, target, data):
    if not n_clicks or not data or not target:
        return "", no_update
    df = pd.DataFrame(data)
    cat_cols = df.select_dtypes(include="object").columns.drop(target)
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
    return f"One-hot encoding applied to {len(cat_cols)} columns.", df.to_dict('records')

@app.callback(
    Output("download-encoded-data", "data"),
    Input("download-encoded-btn", "n_clicks"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def download_encoded(n_clicks, data):
    if not n_clicks or data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "encoded_data.csv", index=False)

# ------------------------
# Train/Test Split
# ------------------------
@app.callback(
    Output("split-msg", "children"),
    Output("train-data-store", "data"),
    Output("test-data-store", "data"),
    Input("btn-split", "n_clicks"),
    State("class-var-dropdown", "value"),
    State("test-size", "value"),
    State("preprocessing-working-data", "data"),
    prevent_initial_call=True
)
def split_data(n_clicks, target, test_size, data):
    if not n_clicks or not data or not target:
        return "Please complete encoding and select a target variable first.", None, None
    
    try:
        df = pd.DataFrame(data)
        
        # Check if target exists
        if target not in df.columns:
            return f"Target variable '{target}' not found in data.", None, None
        
        # Encode target if it's categorical
        le = LabelEncoder()
        df[target] = le.fit_transform(df[target])
        
        # Split features and target
        X = df.drop(columns=[target])
        y = df[target]
        
        # Perform train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Combine X and y back together for download
        train_df = X_train.copy()
        train_df[target] = y_train
        
        test_df = X_test.copy()
        test_df[target] = y_test
        
        msg = (f"Train/Test Split complete ({int((1-test_size)*100)}/{int(test_size*100)}). "
               f"Train shape: {train_df.shape}, Test shape: {test_df.shape}")
        
        return msg, train_df.to_dict('records'), test_df.to_dict('records')
    
    except Exception as e:
        return f"Error during split: {str(e)}", None, None

# ------------------------
# Download Train Data
# ------------------------
@app.callback(
    Output("download-train-data", "data"),
    Input("download-train-btn", "n_clicks"),
    State("train-data-store", "data"),
    prevent_initial_call=True
)
def download_train(n_clicks, data):
    if not n_clicks or data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "train_data.csv", index=False)

# ------------------------
# Download Test Data
# ------------------------
@app.callback(
    Output("download-test-data", "data"),
    Input("download-test-btn", "n_clicks"),
    State("test-data-store", "data"),
    prevent_initial_call=True
)
def download_test(n_clicks, data):
    if not n_clicks or data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "test_data.csv", index=False)

