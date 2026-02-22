import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/mine_icon.svg", height="28px"), width="auto"),
                            dbc.Col(dbc.NavbarBrand("⛏ MineVision Dashboard", className="navbar-brand")),
                        ],
                        align="center",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Resumen", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("Producción", href="/produccion", active="exact")),
                            dbc.NavItem(dbc.NavLink("Equipos", href="/equipos", active="exact")),
                            dbc.NavItem(dbc.NavLink("Seguridad", href="/seguridad", active="exact")),
                            dbc.NavItem(dbc.NavLink("Costos", href="/costos", active="exact")),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        dark=True,
        sticky="top",
        className="navbar",
    )
