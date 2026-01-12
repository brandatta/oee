import streamlit as st
from datetime import datetime
from pathlib import Path

# ================= CONFIG =================
st.set_page_config(page_title="Calculadora OEE", layout="wide")

# ================= ESTILOS =================
st.markdown(
    """
<style>
.kpi-card {border-radius: 16px; padding: 14px 16px; background: #f7f7f8; border: 1px solid #e9eaee}
.kpi-title {font-size: 13px; color: #555; margin-bottom: 4px}
.kpi-value {font-size: 26px; font-weight: 700}
.small-muted {font-size:12px; color:#777}
.ok {color:#107c41}
.mid {color:#c77d00}
.bad {color:#b00020}
.note {background:#fff7e6; border:1px solid #ffe1ac; padding:12px 14px; border-radius:12px}
.formula {background:#eef6ff; border:1px solid #d3e6ff; padding:12px 14px; border-radius:12px}

/* === Fondo verde claro en FO1 y FO2 === */
section[data-testid="stSidebar"] input[aria-label="Factor Operativo FO1"],
section[data-testid="stSidebar"] input[aria-label="Factor Operativo FO2"] {
  background-color: #e9f8ef !important;
  border-radius: 6px !important;
}

/* Borde del contenedor */
section[data-testid="stSidebar"] div[data-baseweb="input"] input[aria-label="Factor Operativo FO1"],
section[data-testid="stSidebar"] div[data-baseweb="input"] input[aria-label="Factor Operativo FO2"] {
  box-shadow: inset 0 0 0 1px #bde5c1 !important;
}

/* Color del texto */
section[data-testid="stSidebar"] input[aria-label="Factor Operativo FO1"],
section[data-testid="stSidebar"] input[aria-label="Factor Operativo FO2"] {
  color: #285c36 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ================= FUNCIONES =================
def clamp01(x: float) -> float:
    return max(0.0, min(float(x), 1.0))


def calc_oee(
    tiempo_plan: float,
    tiempo_paro: float,
    ciclo_ideal_seg_un: float,
    piezas_totales: int,
    piezas_buenas: int,
    fo1: float,
    fo2: float,
    cap_at_100: bool = True,
):
    """
    Definición adoptada (FO penaliza si < 1):
    - Disponibilidad (A) = Tiempo de operación / Tiempo planificado
    - Rendimiento (P) = [(Ciclo ideal × Piezas totales) × (FO1 × FO2)] / (Tiempo operación × 60)
      => Si FO < 1, reduce P (penaliza). Si FO > 1, aumenta P.
    - Calidad (Q) = Piezas buenas / Piezas totales
    - OEE = A × P × Q
    """
    tiempo_operacion = max(tiempo_plan - tiempo_paro, 0.0)

    A_raw = (tiempo_operacion / tiempo_plan) if tiempo_plan > 0 else 0.0

    denom = (tiempo_operacion * 60.0)
    numer = (ciclo_ideal_seg_un * piezas_totales) * (fo1 * fo2)
    P_raw = (numer / denom) if denom > 0 else 0.0

    Q_raw = (piezas_buenas / piezas_totales) if piezas_totales > 0 else 0.0

    OEE_raw = A_raw * P_raw * Q_raw

    if cap_at_100:
        A = clamp01(A_raw)
        P = clamp01(P_raw)
        Q = clamp01(Q_raw)
        OEE = clamp01(A * P * Q)
    else:
        A, P, Q, OEE = A_raw, P_raw, Q_raw, OEE_raw

    return A, P, Q, OEE, tiempo_operacion, A_raw, P_raw, Q_raw, OEE_raw


# ================= SIDEBAR =================
st.sidebar.markdown("<div style='margin-top:-55px; text-align:center;'></div>", unsafe_allow_html=True)
logo_paths = [Path("brandatta_logo.png"), Path("assets/brandatta_logo.png")]
for p in logo_paths:
    if p.exists():
        st.sidebar.image(str(p), width=180)
        break
st.sidebar.markdown("<div style='margin-top:-5px'></div>", unsafe_allow_html=True)

st.sidebar.header("Parámetros")

tiempo_plan = st.sidebar.number_input("Tiempo planificado (min)", min_value=0.0, value=480.0)
tiempo_paro = st.sidebar.number_input("Tiempo de paros (min)", min_value=0.0, value=60.0)
ciclo_ideal = st.sidebar.number_input("Ciclo ideal (seg/un)", min_value=0.0, value=1.5)
piezas_totales = st.sidebar.number_input("Piezas totales", min_value=0, value=18000)
piezas_buenas = st.sidebar.number_input("Piezas de Calidad Aprobada", min_value=0, value=17500)

# Factores: permitir penalización (<1) pero evitar 0
fo1 = st.sidebar.number_input("Factor Operativo FO1", min_value=0.1, value=1.0, step=0.1)
fo2 = st.sidebar.number_input("Factor Operativo FO2", min_value=0.1, value=1.0, step=0.1)

cap_at_100 = st.sidebar.toggle("Capear métricas a 100%", value=True)

# ================= VALIDACIONES (UI) =================
warnings = []

if tiempo_plan == 0:
    warnings.append("El **Tiempo planificado** es 0. No se puede calcular Disponibilidad.")
if tiempo_paro > tiempo_plan and tiempo_plan > 0:
    warnings.append("Los **Paros** superan el **Tiempo planificado**. Revisá la carga de datos.")
if piezas_totales > 0 and piezas_buenas > piezas_totales:
    warnings.append("Las **Piezas de Calidad Aprobada** superan las **Piezas totales**. Revisá la carga.")
if ciclo_ideal == 0 and piezas_totales > 0:
    warnings.append("El **Ciclo ideal** es 0. Rendimiento quedará en 0 (revisá el dato).")

if warnings:
    st.sidebar.markdown("### Observaciones")
    for w in warnings:
        st.sidebar.warning(w)

# ================= CÁLCULO =================
A, P, Q, OEE, tiempo_operacion, A_raw, P_raw, Q_raw, OEE_raw = calc_oee(
    tiempo_plan=tiempo_plan,
    tiempo_paro=tiempo_paro,
    ciclo_ideal_seg_un=ciclo_ideal,
    piezas_totales=int(piezas_totales),
    piezas_buenas=int(piezas_buenas),
    fo1=fo1,
    fo2=fo2,
    cap_at_100=cap_at_100,
)

# ================= INTERFAZ =================
st.title("Calculadora de OEE")
st.write(
    "Mide **Disponibilidad (A)**, **Rendimiento (P)**, **Calidad (Q)** y **Factores Operativos (FO1 y FO2)** "
    "para obtener el OEE de tu línea de producción. En esta versión, **FO1 y FO2 ajustan el Rendimiento (P)** "
    "(si FO < 1, penaliza; si FO > 1, mejora)."
)

cols = st.columns(5)

names = ["Disponibilidad (A)", "Rendimiento (P)", "Calidad (Q)", "OEE", "Tiempo Operación (min)"]
vals = [A, P, Q, OEE, tiempo_operacion]
descs = [
    "Operación / Plan",
    "[(Ciclo ideal × Pzas) × (FO1 × FO2)] / (Operación × 60)",
    "Buenas / Totales",
    "A × P × Q",
    "Plan − Paros",
]

for c, name, val, desc in zip(cols, names, vals, descs):
    if name == "Tiempo Operación (min)":
        color = "ok"
        val_txt = f"{val:.2f}"
    else:
        color = "ok" if val >= 0.85 else ("mid" if val >= 0.6 else "bad")
        val_txt = f"{val*100:.2f}%"

    c.markdown(
        f"""
        <div class='kpi-card'>
          <div class='kpi-title'>{name}</div>
          <div class='kpi-value {color}'>{val_txt}</div>
          <div class='small-muted'>{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Auditoría si cap está activo y el raw excede 100%
if cap_at_100:
    over = []
    if A_raw > 1:
        over.append(f"Disponibilidad sin cap: {A_raw*100:.2f}%")
    if P_raw > 1:
        over.append(f"Rendimiento sin cap: {P_raw*100:.2f}%")
    if Q_raw > 1:
        over.append(f"Calidad sin cap: {Q_raw*100:.2f}%")
    if OEE_raw > 1:
        over.append(f"OEE sin cap: {OEE_raw*100:.2f}%")

    if over:
        st.info(
            "Algunas métricas superan 100% con los datos ingresados. Se aplicó cap a 100% para lectura operativa. "
            "Valores sin cap:\n- " + "\n- ".join(over)
        )

# ================= CONCEPTOS =================
st.subheader("Conceptos")
st.markdown(
    """
<div class='formula'><b>Disponibilidad (A)</b> = Tiempo de operación / Tiempo planificado</div>
<div class='formula'><b>Rendimiento (P)</b> = [(Ciclo ideal × Piezas totales) × (FO1 × FO2)] / (Tiempo de operación × 60)</div>
<div class='formula'><b>Calidad (Q)</b> = Piezas de Calidad Aprobada / Piezas totales</div>
<div class='formula'><b>Factores Operativos (FO1 y FO2)</b> = Ajustes operativos que impactan el cálculo de <b>Rendimiento (P)</b> (FO &lt; 1 penaliza; FO &gt; 1 mejora).</div>
<div class='note'>
<b>OEE = A × P × Q</b>
</div>
""",
    unsafe_allow_html=True,
)

st.caption(f"© {datetime.now().year} — Brandatta • Calculadora OEE")
