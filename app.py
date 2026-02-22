import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

from components.navbar import create_navbar
from pages import overview, produccion, equipos, seguridad, costos, molinos

# ── App ──────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="MineVision Dashboard",
)
server = app.server  # Para gunicorn en producción

# ── Layout principal ─────────────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        create_navbar(),
        html.Div(id="page-content", style={"minHeight": "calc(100vh - 60px)"}),
        html.Footer(
            "MineVision Dashboard · Datos de ejemplo · 2024",
            style={
                "textAlign": "center",
                "padding": ".8rem",
                "fontSize": ".75rem",
                "color": "#8b949e",
                "borderTop": "1px solid #30363d",
                "marginTop": "2rem",
            },
        ),
    ],
    style={"backgroundColor": "#0d1117", "minHeight": "100vh"},
)


# ── Routing ───────────────────────────────────────────────────────────────────
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    routes = {
        "/": overview.layout,
        "/produccion": produccion.layout,
        "/equipos": equipos.layout,
        "/seguridad": seguridad.layout,
        "/costos": costos.layout,
        "/molinos": molinos.layout,
    }
    page_fn = routes.get(pathname, overview.layout)
    return page_fn()


# ── Navbar toggle (mobile) ────────────────────────────────────────────────────
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_navbar(n):
    return n % 2 == 1 if n else False


if __name__ == "__main__":
    app.run(debug=True, port=8050)
