import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ── Fecha base ──────────────────────────────────────────────────────────────
START = datetime(2024, 1, 1)
DAYS = 365
DATES = [START + timedelta(days=i) for i in range(DAYS)]

# ── Producción diaria ────────────────────────────────────────────────────────
def get_production_df():
    trend = np.linspace(4800, 5500, DAYS)
    noise = np.random.normal(0, 200, DAYS)
    tonnage = np.clip(trend + noise, 3000, 7000)

    grade_cu = np.clip(np.random.normal(1.2, 0.15, DAYS), 0.5, 2.0)
    grade_au = np.clip(np.random.normal(0.45, 0.08, DAYS), 0.1, 0.9)

    recovery_cu = np.clip(np.random.normal(88, 3, DAYS), 75, 96)
    recovery_au = np.clip(np.random.normal(82, 4, DAYS), 68, 94)

    return pd.DataFrame({
        "date": DATES,
        "tonnage": tonnage.round(1),
        "grade_cu": grade_cu.round(3),
        "grade_au": grade_au.round(3),
        "recovery_cu": recovery_cu.round(2),
        "recovery_au": recovery_au.round(2),
        "fine_cu_t": (tonnage * grade_cu / 100 * recovery_cu / 100).round(2),
        "fine_au_oz": (tonnage * grade_au / 1000 * recovery_au / 100 * 32.15).round(1),
    })


# ── Equipos ──────────────────────────────────────────────────────────────────
EQUIPMENT = {
    "Palas": ["Pala-01", "Pala-02", "Pala-03"],
    "Camiones": ["CAM-01", "CAM-02", "CAM-03", "CAM-04", "CAM-05", "CAM-06"],
    "Perforadoras": ["PERF-01", "PERF-02"],
    "Chancadoras": ["CHAN-01", "CHAN-02"],
}

def get_equipment_df():
    rows = []
    all_equip = [(t, e) for t, lst in EQUIPMENT.items() for e in lst]
    for tipo, equipo in all_equip:
        for date in DATES:
            disp = np.random.uniform(72, 98)
            util = disp * np.random.uniform(0.75, 0.92)
            maint = 100 - disp
            rows.append({
                "date": date,
                "tipo": tipo,
                "equipo": equipo,
                "disponibilidad": round(disp, 1),
                "utilizacion": round(util, 1),
                "mantenimiento": round(maint, 1),
            })
    return pd.DataFrame(rows)


# ── Seguridad ────────────────────────────────────────────────────────────────
def get_safety_df():
    rows = []
    for date in DATES:
        rows.append({
            "date": date,
            "incidentes": int(np.random.poisson(0.3)),
            "casi_accidentes": int(np.random.poisson(2.5)),
            "dias_sin_accidente": None,  # calculado abajo
            "horas_hombre": int(np.random.normal(12000, 500)),
            "inspecciones": int(np.random.normal(8, 2)),
        })
    df = pd.DataFrame(rows)
    # Calcular días sin accidente acumulados
    counter = 0
    dsas = []
    for inc in df["incidentes"]:
        if inc > 0:
            counter = 0
        else:
            counter += 1
        dsas.append(counter)
    df["dias_sin_accidente"] = dsas
    return df


# ── Costos mensuales ─────────────────────────────────────────────────────────
def get_costs_df():
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    categorias = ["Energía", "Mano de Obra", "Repuestos", "Reactivos", "Combustible", "Otros"]
    base = [1_200_000, 2_800_000, 950_000, 480_000, 720_000, 350_000]
    rows = []
    for m in months:
        for cat, b in zip(categorias, base):
            rows.append({
                "mes": m,
                "categoria": cat,
                "costo": round(b * np.random.uniform(0.90, 1.10)),
            })
    return pd.DataFrame(rows)


# ── KPIs resumen ─────────────────────────────────────────────────────────────
def get_kpis():
    prod = get_production_df()
    safety = get_safety_df()
    return {
        "total_ton": f"{prod['tonnage'].sum():,.0f} t",
        "avg_grade_cu": f"{prod['grade_cu'].mean():.3f} %",
        "total_fine_cu": f"{prod['fine_cu_t'].sum():,.1f} t",
        "total_fine_au": f"{prod['fine_au_oz'].sum():,.0f} oz",
        "dias_sin_accidente": int(safety["dias_sin_accidente"].iloc[-1]),
        "total_incidentes": int(safety["incidentes"].sum()),
    }
