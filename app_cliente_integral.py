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

# 🆕 Calcular el promedio global de todas las dimensiones
df_resultado["promedio_global"] = df_resultado[
    ["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]
].mean(axis=1)

# 🆕 Crear segmentos básicos (por percentiles)
p33 = df_resultado["promedio_global"].quantile(0.33)
p66 = df_resultado["promedio_global"].quantile(0.66)

def clasificar_cliente(valor):
    if valor <= p33:
        return "Malo"
    elif valor <= p66:
        return "Intermedio"
    else:
        return "Bueno"

df_resultado["segmento"] = df_resultado["promedio_global"].apply(clasificar_cliente)

# 🆕 Ordenar por desempeño
df_resultado = df_resultado.sort_values("promedio_global", ascending=False).reset_index(drop=True)

# Mostrar tabla
st.markdown("---")
st.subheader("📋 Segmentación básica de clientes")
st.dataframe(df_resultado, use_container_width=True)

# -----------------------------
# 📊 Distribución de segmentos
# -----------------------------
st.markdown("---")
st.subheader("📊 Distribución de segmentos")

col1, col2 = st.columns(2)

# 🆕 Gráfico de pastel
fig_pie = px.pie(
    df_resultado,
    names="segmento",
    title="Distribución de clientes por segmento",
    color="segmento",
    color_discrete_map={"Bueno": "#6CC24A", "Intermedio": "#FFD700", "Malo": "#E74C3C"}
)
col1.plotly_chart(fig_pie, use_container_width=True)

# 🆕 Gráfico de barras: promedio global por segmento
fig_bar_segmentos = (
    df_resultado.groupby("segmento")["promedio_global"]
    .mean()
    .reset_index()
    .sort_values("promedio_global", ascending=False)
)
fig_bar = px.bar(
    fig_bar_segmentos,
    x="segmento",
    y="promedio_global",
    text_auto=".2f",
    color="segmento",
    color_discrete_map={"Bueno": "#6CC24A", "Intermedio": "#FFD700", "Malo": "#E74C3C"}
)
fig_bar.update_layout(
    template="plotly_white",
    showlegend=False,
    height=400,
    yaxis=dict(range=[0, 1])
)
col2.plotly_chart(fig_bar, use_container_width=True)

# ==========================================================
# 🔍 SECCIÓN: Buscador de cliente (detalle individual)
# ==========================================================

st.markdown("---")
st.subheader("🔎 Consulta detallada de cliente")

# Lista de IDs disponibles
lista_clientes = df_resultado["id_cliente"].tolist()

# Buscador con selectbox
cliente_seleccionado = st.selectbox("Selecciona un cliente:", lista_clientes)

if cliente_seleccionado:

    # -----------------------------
    # 🧮 Datos del cliente seleccionado
    # -----------------------------
    cliente_data = df_resultado[df_resultado["id_cliente"] == cliente_seleccionado].iloc[0]

    st.markdown(f"### 🧍 Cliente seleccionado: `{cliente_seleccionado}`")
    st.markdown(
        f"""
        **Segmento:** {cliente_data['segmento']}  
        **Promedio global:** {cliente_data['promedio_global']:.2f}
        """
    )

    # -----------------------------
    # 📊 Generar indicadores aleatorios por área
    # -----------------------------
    np.random.seed(hash(cliente_seleccionado) % (2**32 - 1))  # fijo por cliente

    indicadores = {
        "brilla": [
            {"indicador": "Número de compras", "valor": np.random.randint(0, 11), "unidad": "compras"},
            {"indicador": "Monto promedio por compra", "valor": round(np.random.uniform(100000, 1000000), -3), "unidad": "COP"},
            {"indicador": "Porcentaje de pagos a tiempo", "valor": round(np.random.uniform(60, 100), 1), "unidad": "%"}
        ],
        "consumo": [
            {"indicador": "Promedio consumo mensual", "valor": round(np.random.uniform(0, 200), 1), "unidad": "m³"},
            {"indicador": "Variabilidad de consumo", "valor": round(np.random.uniform(0, 40), 1), "unidad": "%"},
            {"indicador": "Meses con consumo cero", "valor": np.random.randint(0, 4), "unidad": "meses"}
        ],
        "sad": [
            {"indicador": "Órdenes de servicio realizadas", "valor": np.random.randint(0, 6), "unidad": "órdenes"},
            {"indicador": "Tiempo promedio de atención", "valor": round(np.random.uniform(1, 7), 1), "unidad": "días"},
            {"indicador": "Satisfacción promedio del cliente", "valor": round(np.random.uniform(70, 100), 1), "unidad": "%"}
        ]
    }

    # -----------------------------
    # 🧾 Mostrar indicadores por área
    # -----------------------------
    st.markdown("#### Indicadores detallados por área")

    for area, lista_ind in indicadores.items():
        st.markdown(f"##### 🟢 {area.upper()}")
        cols = st.columns(3)
        for i, ind in enumerate(lista_ind):
            with cols[i]:
                st.metric(
                    label=f"{ind['indicador']}",
                    value=f"{ind['valor']} {ind['unidad']}"
                )
        st.markdown("")  # espacio visual

    # -----------------------------
    # 📊 Mostrar dimensiones normalizadas del cliente
    # -----------------------------
    st.markdown("#### Dimensiones normalizadas del cliente")
    radar_df = cliente_data[
        ["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]
    ].to_frame().T

    categorias = radar_df.columns.tolist()
    valores = radar_df.iloc[0].tolist()

    fig_radar_cliente = go.Figure()
    fig_radar_cliente.add_trace(go.Scatterpolar(
        r=valores + [valores[0]],
        theta=categorias + [categorias[0]],
        fill='toself',
        name=f"Cliente {cliente_seleccionado}",
        line_color="#006699"
    ))
    fig_radar_cliente.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_radar_cliente, use_container_width=True)
