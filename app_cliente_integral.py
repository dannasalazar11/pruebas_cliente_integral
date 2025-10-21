# ============================================
# 🌟 APP CLIENTE INTEGRAL - DEMO STREAMLIT
# ============================================

import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# 🗂️ Cargar los datos
# -----------------------------
@st.cache_data
def cargar_datos():
    df_clientes = pd.read_csv("base_clientes.csv")
    df_dim = pd.read_csv("dimensiones_todas.csv")
    return df_clientes, df_dim

df_clientes, df_dim = cargar_datos()

st.title("🧠 Cliente Integral - Promedios por Dimensión")
st.markdown("Selecciona las **áreas de interés** y el sistema calculará los promedios de dimensiones para los clientes que pertenecen a esas áreas.")

# -----------------------------
# 🎚️ Filtros
# -----------------------------
areas = ["brilla", "consumo", "sad"]
areas_seleccionadas = st.multiselect("Selecciona áreas:", areas, default=["brilla"])

if not areas_seleccionadas:
    st.warning("Selecciona al menos una área para continuar.")
    st.stop()

# -----------------------------
# 🎯 Filtrar clientes que pertenecen a TODAS las áreas seleccionadas
# -----------------------------
filtro = np.logical_and.reduce([df_clientes[a] == 1 for a in areas_seleccionadas])
clientes_filtrados = df_clientes.loc[filtro, "id_cliente"].tolist()

st.markdown(f"**Clientes seleccionados:** {len(clientes_filtrados)} encontrados")

if len(clientes_filtrados) == 0:
    st.info("No hay clientes que pertenezcan simultáneamente a todas las áreas seleccionadas.")
    st.stop()

# -----------------------------
# 📊 Calcular promedios de dimensiones
# -----------------------------
# Filtrar dimensiones solo de las áreas seleccionadas
df_dim_filtrado = df_dim[df_dim["area"].isin(areas_seleccionadas)]
df_dim_filtrado = df_dim_filtrado[df_dim_filtrado["id_cliente"].isin(clientes_filtrados)]

# Agrupar por cliente y calcular promedio de dimensiones
df_resultado = (
    df_dim_filtrado.groupby("id_cliente")[["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]]
    .mean()
    .reset_index()
)

st.subheader("📈 Promedio de dimensiones por cliente")
st.dataframe(df_resultado, use_container_width=True)

# -----------------------------
# 📉 Promedio general de grupo
# -----------------------------
promedios_generales = df_resultado.drop(columns="id_cliente").mean().to_frame("promedio_grupo").T

st.subheader("📊 Promedio general de las dimensiones (grupo)")
st.table(promedios_generales.style.format("{:.2f}"))

# -----------------------------
# 📥 Descargar resultados
# -----------------------------
csv = df_resultado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Descargar resultados como CSV",
    data=csv,
    file_name="promedios_dimensiones_clientes.csv",
    mime="text/csv"
)
