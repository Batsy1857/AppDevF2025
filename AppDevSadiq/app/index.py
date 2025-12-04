import dash
from dash import html, dcc, Input, Output
from app import app
from apps import univariate, bivariate, preprocessing, home, machinelearning

# --------------------------
# GLOBAL STYLES (optional)
# --------------------------
MAIN_BG = "#fafafa"             # very light grey
HEADER_BG = "#e5ebf3"           # soft blue-grey
TEXT_COLOR = "#2a2a2a"          # clean dark text
LINK_COLOR = "#1f5f8b"          # calm blue
LINK_HOVER = "#163f5c"          # slightly darker
BORDER_COLOR = "#dcdcdc"

button_style = {
    "backgroundColor": "#e5ebf3",
    "border": "1px solid #d0d7e1",
    "color": "#2a2a2a",
    "padding": "10px 18px",
    "borderRadius": "6px",
    "fontSize": "15px",
    "cursor": "pointer"
}

app.layout = html.Div(
    style={
        "backgroundColor": MAIN_BG,
        "minHeight": "100vh",
        "padding": "0px 40px",
        "fontFamily": "Arial, sans-serif",
        "color": TEXT_COLOR
    },
    children=[

        # ---------------------------
        # HEADER BAR
        # ---------------------------
        html.Div(
            style={
                "backgroundColor": HEADER_BG,
                "padding": "20px 20px",
                "borderRadius": "8px",
                "marginTop": "20px",
                "marginBottom": "30px",
            },
            children=[
                html.H1(
                    "Welcome to our Data Cleaning Dashboard",
                    style={
                        "margin": "0",
                        "fontWeight": "600",
                        "fontSize": "32px",
                        "textAlign": "center"
                    }
                )
            ]
        ),

        dcc.Location(id='url'),
        
        # ---------------------------
        # SHORT SUBHEADER
        # ---------------------------
        html.H2(
            "Choose from one of the options below:",
            style={
                "marginTop": "10px",
                "fontWeight": "500"
            }
        ),
        html.Hr(style={"borderColor": BORDER_COLOR}),


        # ---------------------------
        # SIMPLE NAVIGATION LINKS
        # ---------------------------
        html.Div(
            style={
                "fontSize": "18px",
                "marginBottom": "25px"
            },
            children=[
                dcc.Link("Home", href="/apps/home", style={"color": LINK_COLOR, "textDecoration": "none"}),
                html.Span(" | "),
                dcc.Link("Preprocessing of Data", href="/apps/preprocessing", style={"color": LINK_COLOR, "textDecoration": "none"}),
                html.Span(" | "),
                dcc.Link("Univariate Analysis", href="/apps/univariate", style={"color": LINK_COLOR, "textDecoration": "none"}),
                html.Span(" | "),
                dcc.Link("Bivariate Analysis", href="/apps/bivariate", style={"color": LINK_COLOR, "textDecoration": "none"}),
                html.Span(" | "),
                dcc.Link("Preparing Data for Machine Learning", href="/apps/machinelearning", style={"color": LINK_COLOR, "textDecoration": "none"}),
            ]
        ),

        # ---------------------------
        # PAGE CONTENT
        # ---------------------------
        html.Div(id='page', style={"padding": "10px 0"}),

        # ---------------------------
        # STORED DATA
        # ---------------------------
        dcc.Store(id="stored-data", storage_type="memory"),
        dcc.Store(id="preprocessing-working-data", storage_type="memory"),
        dcc.Store(id="preprocessing-modified-flag", storage_type="memory", data=False),
    ]
)


@app.callback(
    Output('page', 'children'),
    Input('url', 'pathname')
)
def update_layout(pathname):
    if pathname == '/apps/univariate':
        return univariate.layout
    elif pathname == '/apps/bivariate':
        return bivariate.layout
    elif pathname == '/apps/preprocessing':
        return preprocessing.layout
    elif pathname == '/apps/machinelearning':
        return machinelearning.layout
    else:
        return home.layout

#if __name__ == '__main__':
   # app.run(debug=True, port=8301)

