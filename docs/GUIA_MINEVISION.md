# 📘 Guía Completa – MineVision Dashboard
> Dash · Plotly · Bootstrap · Python  
> Desde cero: conceptos, estructura, datos y hoja de ruta a producción

---

## 1. ¿Qué es este proyecto?

**MineVision Dashboard** es una aplicación web de visualización de datos mineros construida con:

| Librería | Rol |
|---|---|
| `Dash` | Framework web reactivo en Python (sin JavaScript) |
| `Plotly` | Motor de gráficas interactivas |
| `dash-bootstrap-components (dbc)` | Grid system, Navbar, Cards (Bootstrap 5) |
| `pandas` / `numpy` | Transformación de datos |
| `gunicorn` | Servidor WSGI para producción |

**El dashboard actual tiene 5 páginas:**  
`/` Resumen · `/produccion` · `/equipos` · `/seguridad` · `/costos`

---

## 2. Arquitectura del proyecto

```
mining-dashboard/
│
├── app.py                  ← Punto de entrada. Define la app, layout raíz y routing
│
├── pages/                  ← Una página = un archivo Python
│   ├── overview.py         → /
│   ├── produccion.py       → /produccion
│   ├── equipos.py          → /equipos
│   ├── seguridad.py        → /seguridad
│   └── costos.py           → /costos
│
├── components/
│   └── navbar.py           ← Barra de navegación (compartida entre páginas)
│
├── data/
│   └── mining_data.py      ← TODA la lógica de datos. Genera DataFrames con numpy/pandas
│
├── assets/
│   └── style.css           ← CSS global (variables, kpi-card, chart-card, etc.)
│
└── requirements.txt
```

**Flujo de una petición:**
```
Usuario hace click en "Producción"
  → URL cambia a /produccion
    → Callback display_page() en app.py detecta pathname
      → Llama produccion.layout()
        → layout() llama get_production_df()
          → Crea figuras Plotly
            → Retorna html.Div con los gráficos
              → Dash renderiza en el navegador
```

---

## 3. Conceptos clave de Dash

### 3.1 La App

```python
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],   # Tema Bootstrap oscuro
    suppress_callback_exceptions=True,            # Necesario para multi-página
)
server = app.server   # Expone el servidor Flask subyacente (para gunicorn)
```

### 3.2 El Layout

El **layout** es el árbol HTML de tu app. Se construye con componentes Python:

```python
# Dash convierte esto en HTML real
html.Div([                          # → <div>
    html.H1("Título"),              # → <h1>Título</h1>
    html.P("Párrafo"),              # → <p>Párrafo</p>
    dcc.Graph(figure=mi_figura),    # → <div> con el gráfico Plotly
    dbc.Row([                       # → <div class="row">
        dbc.Col(..., md=6),         # → <div class="col-md-6">
    ])
])
```

**Regla de oro:** Todo lo que en HTML sería un atributo, en Dash es un parámetro keyword.  
`<div style="color: red">` → `html.Div(style={"color": "red"})`  
`<div class="kpi-card">` → `html.Div(className="kpi-card")`

### 3.3 Callbacks (interactividad)

Los callbacks conectan **Inputs** (el usuario hace algo) con **Outputs** (algo cambia en pantalla):

```python
@app.callback(
    Output("page-content", "children"),   # → modifica el "children" del Div con id="page-content"
    Input("url", "pathname")              # → se dispara cuando cambia la URL
)
def display_page(pathname):
    if pathname == "/produccion":
        return produccion.layout()
    return overview.layout()
```

**Anatomía de un callback:**
- `Output(id, propiedad)` — qué componente y qué propiedad se actualiza
- `Input(id, propiedad)` — qué componente dispara el callback cuando cambia
- `State(id, propiedad)` — valor que se lee pero NO dispara el callback

### 3.4 dcc.Location — Routing manual

```python
dcc.Location(id="url", refresh=False)
```
Este componente "invisible" expone la URL actual como `pathname`. El callback de routing en `app.py` la lee y decide qué página renderizar.

---

## 4. Cómo funcionan los datos

### 4.1 Datos actuales: generados con NumPy (datos de ejemplo)

Todo está en `data/mining_data.py`. Cada función retorna un **DataFrame de Pandas**:

```
get_production_df()  → 365 filas (un año diario) con tonelaje, leyes, recuperación
get_equipment_df()   → ~4700 filas (13 equipos × 365 días) con disponibilidad y utilización
get_safety_df()      → 365 filas con incidentes, casi-accidentes, horas-hombre
get_costs_df()       → 72 filas (12 meses × 6 categorías) con costos por categoría
get_kpis()           → dict con KPIs resumen del año
```

**¿Por qué numpy.random con seed fija?**  
`np.random.seed(42)` garantiza que los datos sean siempre los mismos al arrancar.  
Simula datos realistas con tendencias, ruido y correlaciones.

### 4.2 Cómo conectar datos reales

Para reemplazar los datos simulados por datos reales, solo hay que modificar las funciones en `mining_data.py`:

**Opción A – CSV/Excel:**
```python
def get_production_df():
    df = pd.read_csv("data/produccion_2024.csv", parse_dates=["date"])
    return df
```

**Opción B – Base de datos SQL:**
```python
import sqlalchemy

engine = sqlalchemy.create_engine("postgresql://user:pass@host/db")

def get_production_df():
    return pd.read_sql("SELECT * FROM produccion WHERE year=2024", engine)
```

**Opción C – API REST:**
```python
import requests

def get_production_df():
    r = requests.get("https://api.mi-mina.com/produccion?year=2024")
    return pd.DataFrame(r.json()["data"])
```

El resto del código (páginas, gráficos) no necesita cambiar — solo la fuente de datos.

---

## 5. Cómo crear una nueva página desde cero

### Paso 1 — Crear el archivo de página

Crear `pages/rendimiento.py`:

```python
# pages/rendimiento.py

import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_production_df   # importar los datos que necesitas

# Constantes de estilo (copiar del resto de páginas)
CARD_BG = "#161b22"
GRID_COLOR = "#30363d"

def plot_cfg(fig, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#c9d1d9", size=11),
        title=dict(text=title, font=dict(size=13, color="#8b949e")),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def layout():
    # 1. Cargar datos
    prod = get_production_df()

    # 2. Crear figura Plotly
    fig = px.line(
        prod.tail(90),
        x="date",
        y="recovery_cu",
        title="Recuperación Cu – Últimos 90 Días",
        labels={"recovery_cu": "Recuperación (%)", "date": "Fecha"},
    )
    plot_cfg(fig)

    # 3. Retornar HTML
    return html.Div([
        html.Div([
            html.H2("Rendimiento"),
            html.P("Análisis de rendimiento operacional"),
        ], className="page-header"),

        dbc.Row([
            dbc.Col(
                html.Div([
                    dcc.Graph(figure=fig, config={"displayModeBar": False}),
                ], className="chart-card"),
                md=12,
            ),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
```

### Paso 2 — Registrar la página en app.py

```python
# En app.py, agregar el import:
from pages import overview, produccion, equipos, seguridad, costos, rendimiento

# En el dict de routes:
routes = {
    "/": overview.layout,
    "/produccion": produccion.layout,
    "/equipos": equipos.layout,
    "/seguridad": seguridad.layout,
    "/costos": costos.layout,
    "/rendimiento": rendimiento.layout,   # ← NUEVO
}
```

### Paso 3 — Agregar al navbar

```python
# En components/navbar.py, dentro de dbc.Nav([...]):
dbc.NavItem(dbc.NavLink("Rendimiento", href="/rendimiento", active="exact")),
```

**¡Listo!** La nueva página aparecerá en el menú y será accesible en `/rendimiento`.

---

## 6. Cómo crear nuevos gráficos

### 6.1 Tipos de gráficos más usados

#### Línea simple
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_scatter(
    x=df["date"],
    y=df["tonelaje"],
    name="Tonelaje",
    line=dict(color="#58a6ff", width=2),
    mode="lines",           # "lines", "markers", "lines+markers"
)
```

#### Barras
```python
fig.add_bar(
    x=df["mes"],
    y=df["costo"],
    name="Costo",
    marker_color="#e8a020",
)
```

#### Barras apiladas
```python
fig.update_layout(barmode="stack")   # "stack" | "group" | "overlay"
```

#### Doble eje Y
```python
fig.add_scatter(x=df["date"], y=df["tonelaje"], name="Tonelaje", yaxis="y")
fig.add_scatter(x=df["date"], y=df["ley_cu"],   name="Ley Cu",   yaxis="y2")
fig.update_layout(
    yaxis=dict(title="Tonelaje (t)"),
    yaxis2=dict(title="Ley Cu (%)", overlaying="y", side="right"),
)
```

#### Gauge / Indicador
```python
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=85,
    title={"text": "Disponibilidad (%)"},
    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#2ea44f"}},
))
```

#### Heatmap
```python
import plotly.express as px

fig = px.imshow(
    dataframe_pivoteado,
    color_continuous_scale="YlOrBr",
    labels=dict(x="Semana", y="Equipo", color="Valor"),
)
```

#### Scatter con color y tamaño
```python
fig = px.scatter(
    df,
    x="tonelaje",
    y="ley_cu",
    color="recuperacion",           # colorea por valor numérico
    size="costo",                   # tamaño de puntos
    color_continuous_scale="Viridis",
)
```

#### Boxplot por categoría
```python
fig = px.box(
    df,
    x="trimestre",
    y="ley_cu",
    color="trimestre",
)
```

### 6.2 Líneas de referencia
```python
fig.add_hline(y=85, line_dash="dash", line_color="#da3633",
              annotation_text="Meta 85%")
fig.add_vline(x="2024-06-01", line_dash="dot", line_color="#58a6ff")
```

### 6.3 Envolver el gráfico en la UI
```python
# Siempre seguir este patrón:
dbc.Col(
    html.Div([
        html.Div("Título del gráfico", className="chart-title"),  # opcional
        dcc.Graph(figure=mi_figura, config={"displayModeBar": False}),
    ], className="chart-card"),
    md=6,   # ancho: 1-12 (Bootstrap grid de 12 columnas)
)
```

---

## 7. Cómo agregar datos al módulo data/mining_data.py

Para añadir un nuevo dataset (ej: calidad de agua, vibración, clima):

```python
# En data/mining_data.py

def get_water_quality_df():
    """Calidad de agua en pozas de proceso."""
    rows = []
    for date in DATES:
        rows.append({
            "date": date,
            "ph": round(np.random.normal(7.5, 0.4), 2),
            "solidos_suspendidos": round(np.random.normal(120, 20), 1),   # mg/L
            "cianuro_libre": round(np.random.normal(0.8, 0.15), 3),       # mg/L
        })
    return pd.DataFrame(rows)
```

Luego importar en la página que lo necesite:
```python
from data.mining_data import get_water_quality_df
```

---

## 8. Interactividad avanzada: Callbacks en páginas

### 8.1 Filtro por rango de fechas

Para agregar un filtro interactivo dentro de una página, el callback debe estar en `app.py` (o en un módulo separado) porque Dash registra los callbacks globalmente.

```python
# En app.py (al final, antes del if __name__ == "__main__")

from dash import Input, Output, State
import plotly.express as px
from data.mining_data import get_production_df

@app.callback(
    Output("grafico-filtrado", "figure"),
    Input("dropdown-trimestre", "value"),
)
def filtrar_por_trimestre(trimestre):
    prod = get_production_df()
    prod["trimestre"] = "T" + pd.to_datetime(prod["date"]).dt.quarter.astype(str)
    if trimestre:
        prod = prod[prod["trimestre"] == trimestre]
    fig = px.line(prod, x="date", y="tonnage", template="plotly_dark")
    return fig
```

Y en la página correspondiente:
```python
# En la función layout()
dcc.Dropdown(
    id="dropdown-trimestre",
    options=[{"label": f"T{i}", "value": f"T{i}"} for i in range(1, 5)],
    value=None,
    placeholder="Todos los trimestres",
    style={"backgroundColor": "#161b22", "color": "#c9d1d9"},
),
dcc.Graph(id="grafico-filtrado"),
```

### 8.2 DatePickerRange
```python
dcc.DatePickerRange(
    id="date-picker",
    start_date="2024-01-01",
    end_date="2024-12-31",
    display_format="DD/MM/YYYY",
),
```

---

## 9. CSS y estilos: cómo personalizar

### Variables CSS disponibles (en assets/style.css)
```css
--bg-dark:    #0d1117   /* Fondo principal */
--bg-card:    #161b22   /* Fondo de tarjetas */
--accent:     #e8a020   /* Dorado – color principal */
--accent2:    #2ea44f   /* Verde */
--text:       #c9d1d9   /* Texto principal */
--text-muted: #8b949e   /* Texto secundario */
--border:     #30363d   /* Bordes */
```

### Clases CSS reutilizables
- `kpi-card` — tarjeta de KPI con hover effect
- `kpi-value` — número grande del KPI
- `kpi-label` — etiqueta pequeña del KPI
- `chart-card` — contenedor de gráfico con fondo oscuro y borde
- `chart-title` — título pequeño en mayúsculas arriba del gráfico
- `page-header` — header con borde izquierdo dorado
- `badge-safe` / `badge-warn` — badges de estado

### Agregar nuevas clases
Solo agrega al archivo `assets/style.css`. Dash lo carga automáticamente.

```css
.mi-nueva-clase {
    background: var(--bg-card2);
    border-radius: 8px;
    padding: 1rem;
}
```

---

## 10. Hoja de ruta: de prototipo a producto real

### Fase 1 — Datos reales (inmediato)

| Tarea | Qué hacer |
|---|---|
| **Conectar DB** | Reemplazar funciones en `mining_data.py` con `pd.read_sql()` usando SQLAlchemy |
| **Variables de entorno** | Usar `python-dotenv` para credenciales (`DB_HOST`, `DB_PASS`) |
| **Cache de queries** | Usar `@cache.memoize()` de `flask-caching` para no repetir queries en cada navegación |
| **Datos en tiempo real** | Agregar `dcc.Interval` que dispara callbacks cada N segundos para actualizar gráficos |

```python
# Tiempo real con dcc.Interval
dcc.Interval(id="interval", interval=30_000, n_intervals=0)  # cada 30s

@app.callback(Output("kpi-tonelaje", "children"), Input("interval", "n_intervals"))
def actualizar_kpi(_):
    prod = get_production_df()  # ahora leería de BD en tiempo real
    return f"{prod['tonnage'].iloc[-1]:,.0f} t"
```

### Fase 2 — Infraestructura (semanas 2-4)

| Área | Stack recomendado |
|---|---|
| **Base de datos** | PostgreSQL + TimescaleDB (series de tiempo) |
| **ORM / queries** | SQLAlchemy + Alembic para migraciones |
| **Cache** | Redis + flask-caching |
| **Autenticación** | `dash-auth` (básica) o Flask-Login + JWT |
| **Servidor** | Gunicorn + Nginx (ya hay `server = app.server` en app.py) |
| **Contenedor** | Docker + docker-compose |

**Estructura recomendada con cache:**
```python
# app.py
from flask_caching import Cache

cache = Cache(app.server, config={"CACHE_TYPE": "redis", "CACHE_REDIS_URL": REDIS_URL})

# En mining_data.py
@cache.memoize(timeout=300)   # cachea 5 minutos
def get_production_df():
    return pd.read_sql(...)
```

### Fase 3 — Multi-usuario y seguridad

```python
# Agregar autenticación básica
from dash_auth import BasicAuth

VALID_USERS = {"admin": "password123", "operador": "pass456"}
BasicAuth(app, VALID_USERS)
```

Para producción real: sistema de roles (admin, supervisor, visualizador) con base de datos de usuarios y sesiones.

### Fase 4 — Alertas y notificaciones

- **Alertas en dashboard:** `dbc.Alert` condicional cuando KPI cruza umbral
- **Emails/SMS:** `smtplib` o Twilio cuando TRIR > 1.5 o disponibilidad < 80%
- **Reportes automáticos:** `kaleido` para exportar figuras Plotly a PNG/PDF, `reportlab` para PDFs

### Fase 5 — Escalabilidad

| Problema | Solución |
|---|---|
| Muchos usuarios simultáneos | Gunicorn con workers: `gunicorn -w 4 app:server` |
| Datos muy grandes (>1M filas) | DuckDB para analítica, o pre-agregar en DB |
| Deploy en nube | Render.com, Railway, AWS App Runner, Google Cloud Run |
| Multi-sitio / multi-mina | Dropdown selector de mina, datos particionados por `site_id` |
| Dash Pages (routing nativo) | Migrar a `dash.register_page()` en vez del routing manual actual |

### Arquitectura objetivo (producto real)

```
[Sensores / SCADA / ERP]
         ↓
[ETL / Ingesta] → PostgreSQL + TimescaleDB
         ↓
[API FastAPI (opcional)] ← autenticación, validación
         ↓
[mining_data.py] ← consultas con caché Redis
         ↓
[Dash App] → Gunicorn → Nginx → HTTPS
         ↓
[Usuarios: Gerencia, Supervisores, Operadores]
```

---

## 11. Comandos útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr en desarrollo
python app.py

# Correr con gunicorn (producción)
gunicorn app:server -w 4 --bind 0.0.0.0:8050

# Agregar nueva dependencia
pip install nueva-lib && pip freeze > requirements.txt
```

---

## 12. Checklist para agregar una nueva página

```
[ ] 1. Crear pages/mi_pagina.py con función layout()
[ ] 2. Agregar import en app.py
[ ] 3. Agregar ruta en el dict routes en app.py
[ ] 4. Agregar NavLink en components/navbar.py
[ ] 5. Si necesita datos nuevos: agregar función en data/mining_data.py
[ ] 6. Si necesita callbacks interactivos: agregar @app.callback en app.py
[ ] 7. Verificar que arranca sin errores: python app.py
```

---

*Guía generada para MineVision Dashboard · Febrero 2026*
