import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_equipment_df

PLOTLY_TEMPLATE = "plotly_dark"
CARD_BG = "#161b22"
GRID_COLOR = "#30363d"

def plot_cfg(fig):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#c9d1d9", size=11),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def layout():
    df = get_equipment_df()

    # Promedios por equipo (todo el año)
    equip_avg = df.groupby(["tipo", "equipo"]).agg(
        disponibilidad=("disponibilidad", "mean"),
        utilizacion=("utilizacion", "mean"),
        mantenimiento=("mantenimiento", "mean"),
    ).reset_index().round(1)

    # ── Fig 1: Disponibilidad por equipo (horizontal bar) ────────────────────
    fig_disp = px.bar(
        equip_avg.sort_values("disponibilidad"),
        x="disponibilidad", y="equipo", color="tipo",
        orientation="h",
        color_discrete_sequence=["#e8a020", "#2ea44f", "#58a6ff", "#da3633"],
        title="Disponibilidad Promedio por Equipo (%)",
        labels={"disponibilidad": "Disponibilidad (%)", "equipo": ""},
    )
    fig_disp.add_vline(x=85, line_dash="dash", line_color="#c9d1d9",
                       annotation_text="Meta 85%", annotation_font_color="#c9d1d9")
    plot_cfg(fig_disp)

    # ── Fig 2: Utilización vs Disponibilidad scatter ─────────────────────────
    fig_ud = px.scatter(
        equip_avg, x="disponibilidad", y="utilizacion",
        color="tipo", size="mantenimiento",
        text="equipo",
        color_discrete_sequence=["#e8a020", "#2ea44f", "#58a6ff", "#da3633"],
        title="Utilización vs Disponibilidad",
        labels={"disponibilidad": "Disponibilidad (%)", "utilizacion": "Utilización (%)"},
    )
    fig_ud.update_traces(textposition="top center", textfont_size=9)
    fig_ud.add_vline(x=85, line_dash="dash", line_color="#e8a020")
    fig_ud.add_hline(y=75, line_dash="dash", line_color="#58a6ff")
    plot_cfg(fig_ud)

    # ── Fig 3: Tendencia mensual disponibilidad palas ────────────────────────
    palas = df[df["tipo"] == "Palas"].copy()
    palas["month"] = pd.to_datetime(palas["date"]).dt.to_period("M").dt.to_timestamp()
    palas_m = palas.groupby(["month", "equipo"])["disponibilidad"].mean().reset_index()

    fig_palas = px.line(
        palas_m, x="month", y="disponibilidad", color="equipo",
        color_discrete_sequence=["#e8a020", "#2ea44f", "#58a6ff"],
        title="Disponibilidad Mensual – Palas",
        markers=True,
        labels={"disponibilidad": "Disponibilidad (%)", "month": "Mes"},
    )
    fig_palas.add_hline(y=85, line_dash="dash", line_color="#da3633",
                        annotation_text="Meta 85%", annotation_font_color="#da3633")
    plot_cfg(fig_palas)

    # ── Fig 4: Tendencia mensual camiones ────────────────────────────────────
    cam = df[df["tipo"] == "Camiones"].copy()
    cam["month"] = pd.to_datetime(cam["date"]).dt.to_period("M").dt.to_timestamp()
    cam_m = cam.groupby(["month", "equipo"])["disponibilidad"].mean().reset_index()

    fig_cam = px.line(
        cam_m, x="month", y="disponibilidad", color="equipo",
        color_discrete_sequence=["#e8a020", "#2ea44f", "#58a6ff", "#da3633", "#9b59b6", "#1abc9c"],
        title="Disponibilidad Mensual – Camiones",
        markers=False,
        labels={"disponibilidad": "Disponibilidad (%)", "month": "Mes"},
    )
    fig_cam.add_hline(y=85, line_dash="dash", line_color="#c9d1d9")
    plot_cfg(fig_cam)

    # ── Fig 5: Pie distribución tiempo por tipo ───────────────────────────────
    tipo_avg = equip_avg.groupby("tipo").agg(
        disponibilidad=("disponibilidad", "mean"),
        mantenimiento=("mantenimiento", "mean"),
    ).reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=tipo_avg["tipo"],
        values=tipo_avg["disponibilidad"],
        hole=0.45,
        marker_colors=["#e8a020", "#2ea44f", "#58a6ff", "#da3633"],
    ))
    fig_pie.update_layout(
        title="Disponibilidad Promedio por Tipo de Equipo",
        paper_bgcolor=CARD_BG,
        font=dict(color="#c9d1d9"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

    # ── Fig 6: Heatmap disponibilidad semanal camiones ───────────────────────
    cam_daily = df[df["tipo"] == "Camiones"].copy()
    cam_daily["week"] = pd.to_datetime(cam_daily["date"]).dt.isocalendar().week.astype(int)
    pivot = cam_daily.pivot_table(
        index="equipo", columns="week", values="disponibilidad", aggfunc="mean"
    ).round(1)
    # Solo primeras 26 semanas para visualización
    pivot = pivot.iloc[:, :26]
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=[[0, "#3d1212"], [0.5, "#3d2f0a"], [1, "#1a4731"]],
        title="Disponibilidad Semanal – Camiones (%)",
        labels=dict(x="Semana", y="Equipo", color="Disp. (%)"),
        zmin=65, zmax=98,
    )
    plot_cfg(fig_heat)

    # ── Tabla resumen KPIs equipo ─────────────────────────────────────────────
    table_rows = []
    for _, row in equip_avg.iterrows():
        color = "#2ea44f" if row["disponibilidad"] >= 85 else "#da3633"
        table_rows.append(
            html.Tr([
                html.Td(row["equipo"], style={"fontWeight": "600"}),
                html.Td(row["tipo"], style={"color": "#8b949e"}),
                html.Td(f"{row['disponibilidad']}%", style={"color": color, "fontWeight": "700"}),
                html.Td(f"{row['utilizacion']}%"),
                html.Td(f"{row['mantenimiento']}%", style={"color": "#e8a020"}),
            ])
        )

    tabla = html.Table(
        [
            html.Thead(html.Tr([
                html.Th("Equipo"), html.Th("Tipo"),
                html.Th("Disponib."), html.Th("Utiliz."), html.Th("Mantenimiento"),
            ], style={"color": "#8b949e", "fontSize": ".8rem", "textTransform": "uppercase"})),
            html.Tbody(table_rows),
        ],
        style={"width": "100%", "fontSize": ".85rem", "borderCollapse": "collapse"},
        className="table-hover",
    )

    return html.Div([
        html.Div([
            html.H2("Equipos"),
            html.P("Monitoreo de disponibilidad, utilización y mantenimiento de flota · 2024"),
        ], className="page-header"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_disp, config={"displayModeBar": False})], className="chart-card"), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_pie, config={"displayModeBar": False})], className="chart-card"), md=5),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_palas, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_cam, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_ud, config={"displayModeBar": False})], className="chart-card"), md=5),
            dbc.Col(html.Div([dcc.Graph(figure=fig_heat, config={"displayModeBar": False})], className="chart-card"), md=7),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Resumen por Equipo", className="chart-title"),
                tabla,
            ], className="chart-card"), md=12),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
