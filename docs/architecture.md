# MineVision Dashboard — Documentación de Arquitectura

> Fecha: 2026-02-22 · Stack: Python · Dash · Plotly · Dash Bootstrap Components

---

## Tabla de Contenidos

1. [Estructura del Proyecto](#1-estructura-del-proyecto)
2. [Arquitectura General](#2-arquitectura-general)
3. [Flujo de Inicialización](#3-flujo-de-inicialización)
4. [Capa de Datos (`data/`)](#4-capa-de-datos-data)
5. [Componentes (`components/`)](#5-componentes-components)
6. [Sistema de Routing](#6-sistema-de-routing)
7. [Callbacks de Dash](#7-callbacks-de-dash)
8. [Páginas — Layouts](#8-páginas--layouts)
   - [8.1 Overview (Resumen)](#81-overview-resumen)
   - [8.2 Producción](#82-producción)
   - [8.3 Equipos](#83-equipos)
   - [8.4 Seguridad](#84-seguridad)
   - [8.5 Costos](#85-costos)
9. [Flujo completo de una petición de página](#9-flujo-completo-de-una-petición-de-página)
10. [Mapa de dependencias entre módulos](#10-mapa-de-dependencias-entre-módulos)

---

## 1. Estructura del Proyecto

```
mining-dashboard/
├── app.py                  # Entry-point · instancia Dash · routing · navbar toggle
├── requirements.txt
├── assets/                 # CSS global, íconos SVG (servidos estáticamente por Dash)
├── components/
│   ├── __init__.py
│   └── navbar.py           # Función create_navbar() → dbc.Navbar
├── data/
│   ├── __init__.py
│   └── mining_data.py      # Generadores de DataFrames sintéticos + KPIs
└── pages/
    ├── __init__.py
    ├── overview.py         # Página "Resumen"
    ├── produccion.py       # Página "Producción"
    ├── equipos.py          # Página "Equipos"
    ├── seguridad.py        # Página "Seguridad"
    └── costos.py           # Página "Costos"
```

---

## 2. Arquitectura General

```mermaid
graph TB
    subgraph Browser[Navegador]
        URL[URL pathname]
        DOM[DOM renderizado]
    end

    subgraph DashServer[Servidor Dash]
        APP[app.py Dash instance]
        ROUTER[display_page callback]
        TOGGLE[toggle_navbar callback]
    end

    subgraph Components[components]
        NAV[navbar.py]
    end

    subgraph Pages[pages]
        OV[overview.py]
        PR[produccion.py]
        EQ[equipos.py]
        SEG[seguridad.py]
        CO[costos.py]
    end

    subgraph Data[data]
        DM[mining_data.py]
    end

    URL -->|pathname| ROUTER
    ROUTER -->|/| OV
    ROUTER -->|/produccion| PR
    ROUTER -->|/equipos| EQ
    ROUTER -->|/seguridad| SEG
    ROUTER -->|/costos| CO

    OV --> DM
    PR --> DM
    EQ --> DM
    SEG --> DM
    CO --> DM

    APP --> NAV
    APP --> ROUTER
    APP --> TOGGLE
    OV --> DOM
    PR --> DOM
    EQ --> DOM
    SEG --> DOM
    CO --> DOM
```

---

## 3. Flujo de Inicialización

```mermaid
sequenceDiagram
    participant PY as Python runtime
    participant APP as app.py
    participant NAV as navbar.py
    participant DASH as Dash framework

    PY->>APP: import app
    APP->>DASH: Dash init
    DASH-->>APP: app instance
    APP->>NAV: create_navbar()
    NAV-->>APP: navbar component
    APP->>DASH: set app.layout
    APP->>DASH: register callbacks
    PY->>APP: app.run
    DASH-->>PY: listening :8050
```

---

## 4. Capa de Datos (`data/`)

Todos los datos son **sintéticos** generados en memoria con `numpy` y `pandas`. No hay base de datos ni archivos externos.

### Funciones expuestas

| Función | Retorno | Descripción |
|---|---|---|
| `get_production_df()` | `DataFrame` 365 filas | Tonelaje, leyes Cu/Au, recuperación, finos diarios |
| `get_equipment_df()` | `DataFrame` ~4745 filas | Disponibilidad/utilización/mantenimiento por equipo×día |
| `get_safety_df()` | `DataFrame` 365 filas | Incidentes, casi-accidentes, horas-hombre, días sin accidente |
| `get_costs_df()` | `DataFrame` 72 filas | Costos mensuales por 6 categorías (12 meses × 6) |
| `get_kpis()` | `dict` | Resumen numérico (llama internamente a prod y safety) |

### Modelo de datos

```mermaid
erDiagram
    PRODUCTION {
        date date
        tonnage float
        grade_cu float
        grade_au float
        recovery_cu float
        recovery_au float
        fine_cu_t float
        fine_au_oz float
    }

    EQUIPMENT {
        date date
        tipo string
        equipo string
        disponibilidad float
        utilizacion float
        mantenimiento float
    }

    SAFETY {
        date date
        incidentes int
        casi_accidentes int
        dias_sin_accidente int
        horas_hombre int
        inspecciones int
    }

    COSTS {
        mes date
        categoria string
        costo float
    }
```

### Flujo de generación de datos

```mermaid
flowchart LR
    SEED[Random seed 42] --> DATES[365 days from 2024-01-01]

    DATES --> PROD[get_production_df]
    DATES --> EQUIP[get_equipment_df]
    DATES --> SAFE[get_safety_df]
    DATES --> COSTS[get_costs_df]

    PROD --> KPIS[get_kpis]
    SAFE --> KPIS
```

---

## 5. Componentes (`components/`)

### `navbar.py` — `create_navbar()`

Retorna un `dbc.Navbar` sticky con:
- Logo SVG + brand text
- `dbc.NavbarToggler` (id `navbar-toggler`) para mobile
- `dbc.Collapse` (id `navbar-collapse`) con 5 `NavLink`s

```mermaid
graph LR
    FN[create_navbar] --> NAVBAR[dbc.Navbar]
    NAVBAR --> CONTAINER[Container]
    CONTAINER --> BRAND[Logo + Brand]
    CONTAINER --> TOGGLER[NavbarToggler]
    CONTAINER --> COLLAPSE[Collapse]
    COLLAPSE --> NAV[Nav]
    NAV --> L1[Resumen /]
    NAV --> L2[Produccion /produccion]
    NAV --> L3[Equipos /equipos]
    NAV --> L4[Seguridad /seguridad]
    NAV --> L5[Costos /costos]
```

---

## 6. Sistema de Routing

Dash utiliza `dcc.Location` para leer el pathname del navegador. El callback `display_page` actúa como router SPA.

```mermaid
flowchart TD
    LOC[dcc.Location] -->|pathname| CB[display_page callback]

    CB -->|/| OV[overview.layout]
    CB -->|/produccion| PR[produccion.layout]
    CB -->|/equipos| EQ[equipos.layout]
    CB -->|/seguridad| SEG[seguridad.layout]
    CB -->|/costos| CO[costos.layout]
    CB -->|default| OV

    OV & PR & EQ & SEG & CO -->|html.Div| PC[page-content]
```

> Cada `layout()` se llama **en cada navegación** — los datos se regeneran sincrónicamente.

---

## 7. Callbacks de Dash

La app tiene exactamente **2 callbacks registrados** en `app.py`:

```mermaid
graph LR
    subgraph CB1[Callback 1 - Routing]
        IN1[Input: url.pathname]
        FN1[display_page]
        OUT1[Output: page-content.children]
        IN1 --> FN1 --> OUT1
    end

    subgraph CB2[Callback 2 - Navbar Toggle]
        IN2[Input: navbar-toggler.n_clicks]
        FN2[toggle_navbar]
        OUT2[Output: navbar-collapse.is_open]
        IN2 --> FN2 --> OUT2
    end
```

No hay callbacks reactivos dentro de las páginas — todos los gráficos son **estáticos** (figuras Plotly pre-construidas en `layout()`).

---

## 8. Páginas — Layouts

Cada página sigue el mismo patrón:

```mermaid
flowchart TD
    CALL[layout called] --> DATA[Get DataFrame]
    DATA --> TRANSFORM[Pandas transformations]
    TRANSFORM --> FIGS[Build Plotly figures]
    FIGS --> STYLE[Apply plot config]
    STYLE --> HTML[Return html.Div]
```

---

### 8.1 Overview (Resumen) — `pages/overview.py`

**Datos:** `get_production_df()`, `get_safety_df()`, `get_kpis()`

```mermaid
graph TD
    OV[overview.layout]

    OV --> KPI[KPI Cards Row<br/>6 cards]

    OV --> ROW1[Row1 - 8:4 cols]
    ROW1 --> FIG_TON[Tonnage chart<br/>Bar + Scatter]
    ROW1 --> FIG_GAUGE[Days without<br/>accident gauge]

    OV --> ROW2[Row2 - 6:6 cols]
    ROW2 --> FIG_FINOS[Fine metals chart]
    ROW2 --> FIG_SAFETY[Safety incidents]
```

**Transformaciones clave:**
- Resample diario → mensual con `groupby("month").agg(...)`
- Rolling mean 3 meses para promedio móvil

---

### 8.2 Producción — `pages/produccion.py`

**Datos:** `get_production_df()`

```mermaid
graph TD
    PR[produccion.layout]

    PR --> ROW1[Row1 - 8:4]
    ROW1 --> FIG_DAILY[Daily tonnage]
    ROW1 --> FIG_BOX[Boxplot by quarter]

    PR --> ROW2[Row2 - 6:6]
    ROW2 --> FIG_REC[Recovery percent]
    ROW2 --> FIG_SCATTER[Grade vs tonnage]

    PR --> ROW3[Row3 - 7:5]
    ROW3 --> FIG_ACUM[Accumulated fines]
    ROW3 --> FIG_HEAT[Heat map tonnage]
```

---

### 8.3 Equipos — `pages/equipos.py`

**Datos:** `get_equipment_df()` (4745 filas: 13 equipos × 365 días)

```mermaid
graph TD
    EQ[equipos.layout]

    EQ --> AGG[Aggregate by type]

    AGG --> ROW1[Row1 - 7:5]
    ROW1 --> FIG_DISP[Availability %]
    ROW1 --> FIG_PIE[Pie donut<br/>by type]

    AGG --> ROW2[Row2 - 6:6]
    ROW2 --> FIG_PALAS[Loader trend]
    ROW2 --> FIG_CAM[Truck trend]

    AGG --> ROW3[Row3 - 5:7]
    ROW3 --> FIG_UD[Utilization<br/>vs Availability]
    ROW3 --> FIG_HEAT_EQ[Heat map<br/>availability]

    AGG --> TABLE[Summary table<br/>by equipment]
```

---

### 8.4 Seguridad — `pages/seguridad.py`

**Datos:** `get_safety_df()`

```mermaid
graph TD
    SEG[seguridad.layout]

    SEG --> KPI[KPI Banner<br/>DSA, Incidents, TRIR]

    SEG --> ROW1[Row1 - 8:4]
    ROW1 --> FIG_DSA[Days without<br/>accident]
    ROW1 --> FIG_SUN[Incident<br/>distribution]

    SEG --> ROW2[Row2 - 6:6]
    ROW2 --> FIG_TRIR[TRIR monthly]
    ROW2 --> FIG_CA[Near misses<br/>+ inspections]

    SEG --> ROW3[Row3 - 7:5]
    ROW3 --> FIG_HEAT_SEG[Heat map<br/>incidents]
    ROW3 --> FIG_HH[Hours worked<br/>cumulative]
```

---

### 8.5 Costos — `pages/costos.py`

**Datos:** `get_costs_df()` + `get_production_df()` (para costo/tonelada)

```mermaid
graph TD
    CO[costos.layout]

    CO --> KPI[KPI Banner<br/>Annual cost, Cost/t]

    CO --> ROW1[Row1 - 4:8]
    ROW1 --> FIG_DONUT[Donut<br/>by category]
    ROW1 --> FIG_MONTHLY[Monthly cost]

    CO --> ROW2[Row2 - 6:6]
    ROW2 --> FIG_STACK[Stacked costs<br/>by category]
    ROW2 --> FIG_CPT[Cost per<br/>tonnage]

    CO --> ROW3[Row3 - 7:5]
    ROW3 --> FIG_WF[Waterfall<br/>variation]
    ROW3 --> FIG_SC_CO[Cost vs<br/>tonnage scatter]
```

---

## 9. Flujo completo de una petición de página

Ejemplo: usuario hace clic en "Producción" en la navbar.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Dash as Dash.js
    participant Flask
    participant CB as Callback
    participant Page as Layout
    participant Data as Data Module

    User->>Browser: Click Produccion link
    Browser->>Dash: URL change
    Dash->>Flask: Update component
    Flask->>CB: display_page
    CB->>Page: layout call
    Page->>Data: get dataframe
    Data-->>Page: DataFrame
    Page->>Page: Build figures
    Page-->>CB: Return HTML
    CB-->>Flask: Send JSON
    Flask-->>Dash: Response
    Dash->>Browser: Update DOM
    Browser-->>User: Page rendered
```

---

## 10. Mapa de dependencias entre módulos

```mermaid
graph LR
    APP[app.py]
    NAV[navbar.py]
    OV[overview.py]
    PR[produccion.py]
    EQ[equipos.py]
    SEG[seguridad.py]
    CO[costos.py]
    DM[mining_data.py]
    
    APP --> NAV
    APP --> OV
    APP --> PR
    APP --> EQ
    APP --> SEG
    APP --> CO

    OV --> DM
    PR --> DM
    EQ --> DM
    SEG --> DM
    CO --> DM
    
    APP --> DBC[dash_bootstrap_components]
    OV --> DBC
    PR --> DBC
    EQ --> DBC
    SEG --> DBC
    CO --> DBC
    
    OV --> PLOTLY[plotly]
    PR --> PLOTLY
    EQ --> PLOTLY
    SEG --> PLOTLY
    CO --> PLOTLY
```

---

### Notas de diseño

| Decisión | Razón |
|---|---|
| `suppress_callback_exceptions=True` | El `page-content` se puebla dinámicamente; Dash no puede validar IDs en arranque |
| `server = app.server` | Expone el objeto Flask para despliegue con gunicorn |
| Datos sintéticos en memoria | No requiere BD; reproducibles con `seed(42)` |
| Layouts sin callbacks reactivos | Todos los gráficos se pre-computan al navegar; no hay interactividad intra-página |
| `dcc.Location(refresh=False)` | SPA — navegación sin reload completo de página |
