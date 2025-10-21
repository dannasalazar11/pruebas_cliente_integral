# ============================================
# 🌟 CLIENTE INTEGRAL - DASHBOARD STREAMLIT
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# ⚙️ Configuración general
# -----------------------------
st.set_page_config(page_title="Cliente Integral", layout="wide")
st.title("Cliente Integral")

# -----------------------------
# 🗂️ Cargar datos
# -----------------------------
@st.cache_data
def cargar_datos():
    df_clientes = pd.read_csv("base_clientes.csv")
    df_dim = pd.read_csv("dimensiones_todas.csv")
    return df_clientes, df_dim

df_clientes, df_dim = cargar_datos()

# -----------------------------
# 🎚️ Filtros en el sidebar
# -----------------------------
st.sidebar.header("⚙️ Configuración")
st.sidebar.markdown("Selecciona las áreas de interés:")

areas = ["brilla", "consumo", "sad"]
areas_seleccionadas = st.sidebar.multiselect("Áreas", areas, default=["brilla"])

if not areas_seleccionadas:
    st.warning("Selecciona al menos una área en el panel izquierdo.")
    st.stop()

# -----------------------------
# 🎯 Filtrado de clientes
# -----------------------------
filtro = np.logical_and.reduce([df_clientes[a] == 1 for a in areas_seleccionadas])
clientes_filtrados = df_clientes.loc[filtro, "id_cliente"].tolist()

col_info, col_img = st.columns([0.8, 0.2])
col_info.markdown(f"### Clientes seleccionados: {len(clientes_filtrados)}")
col_info.caption(f"Mostrando clientes que pertenecen a **todas las áreas seleccionadas:** {', '.join(areas_seleccionadas)}")

if len(clientes_filtrados) == 0:
    st.info("No hay clientes que pertenezcan simultáneamente a todas las áreas seleccionadas.")
    st.stop()

# -----------------------------
# 📊 Calcular promedios por cliente
# -----------------------------
df_dim_filtrado = df_dim[
    (df_dim["area"].isin(areas_seleccionadas)) &
    (df_dim["id_cliente"].isin(clientes_filtrados))
]

df_resultado = (
    df_dim_filtrado.groupby("id_cliente")[["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]]
    .mean()
    .reset_index()
)

# -----------------------------
# 📈 Promedios generales del grupo
# -----------------------------
promedios_generales = df_resultado.drop(columns="id_cliente").mean().to_frame("promedio").T

# -----------------------------
# 🧾 Layout principal
# -----------------------------
st.markdown("---")
st.subheader("📋 Promedios por cliente")
st.dataframe(df_resultado, use_container_width=True)

# Sección visual
st.markdown("---")
st.subheader("📊 Resumen visual de las dimensiones")

col1, col2 = st.columns(2)

# -----------------------------
# 📉 1. Radar Chart - perfil promedio
# -----------------------------
categorias = list(promedios_generales.columns)
valores = list(promedios_generales.iloc[0])

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=valores + [valores[0]],
    theta=categorias + [categorias[0]],
    fill='toself',
    name='Promedio grupo',
    line_color="#0088cc"
))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1]),
    ),
    showlegend=False,
    template="plotly_white",
    height=400,
    margin=dict(l=20, r=20, t=20, b=20)
)
col1.plotly_chart(fig_radar, use_container_width=True)
col1.caption("Perfil promedio del grupo por dimensión")

# -----------------------------
# 📊 2. Bar Chart - comparación de dimensiones
# -----------------------------
fig_bar = px.bar(
    promedios_generales.melt(var_name="Dimensión", value_name="Promedio"),
    x="Dimensión", y="Promedio",
    text_auto=".2f",
    color="Dimensión",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_bar.update_layout(
    template="plotly_white",
    showlegend=False,
    height=400,
    yaxis=dict(range=[0, 1])
)
col2.plotly_chart(fig_bar, use_container_width=True)
col2.caption("Comparativo de promedios por dimensión")

# -----------------------------
# 📥 Descargar resultados
# -----------------------------
st.markdown("---")
st.subheader("⬇️ Descargar resultados")
csv = df_resultado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Descargar promedios por cliente (.csv)",
    data=csv,
    file_name="promedios_dimensiones_clientes.csv",
    mime="text/csv"
)

st.caption("Versión demo — Proyecto Cliente Integral")
