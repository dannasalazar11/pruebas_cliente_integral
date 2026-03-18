import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from features.valoracion_integral.formatters import human_format


def render_penetracion_servicios_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos para clientes por servicio.")
        return

    df = df.copy()
    df["clientes"] = df["clientes"].fillna(0)
    df = df.sort_values("clientes", ascending=True)
    palette = ["#DCEBFA", "#B8D8F8", "#8EC5F4", "#5CA9E6", "#0B74C8"]
    colors = palette[-len(df):]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["clientes"],
            y=df["servicio"],
            orientation="h",
            text=[human_format(value) for value in df["clientes"]],
            textposition="outside",
            marker=dict(
                color=colors,
                line=dict(color="#0B74C8", width=0),
            ),
            hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#E8EEF5",
            zeroline=False,
            showline=False,
            tickfont=dict(color="#7A869A"),
        ),
        yaxis=dict(title="", showgrid=False, tickfont=dict(size=15, color="#5B657A")),
        showlegend=False,
        bargap=0.28,
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_numero_servicios_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos para número de servicios por cliente.")
        return

    df = df.copy()
    df["NumeroServicios"] = df["NumeroServicios"].astype(int)
    df["clientes"] = df["clientes"].fillna(0)
    df["label"] = df["NumeroServicios"].apply(
        lambda value: f"{value} servicio" if value == 1 else f"{value} servicios"
    )

    color_map = {1: "#D94F4F", 2: "#0B74C8", 3: "#8EC5F4", 4: "#7A5AF8", 5: "#16A34A"}
    colors = [color_map.get(value, "#CBD5E1") for value in df["NumeroServicios"]]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["label"],
                values=df["clientes"],
                hole=0.58,
                sort=False,
                marker=dict(colors=colors, line=dict(color="white", width=2)),
                textinfo="percent",
                textfont=dict(size=15, color="#1F2937"),
                hovertemplate="<b>%{label}</b><br>Clientes: %{value:,}<br>Participación: %{percent}<extra></extra>",
            )
        ]
    )

    total_clientes = int(df["clientes"].sum())
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{human_format(total_clientes)}</b><br><span style='font-size:12px;color:#7A869A'>clientes</span>",
                x=0.5,
                y=0.5,
                font=dict(size=20, color="#1E293B"),
                showarrow=False,
            )
        ],
        legend=dict(
            orientation="v",
            y=0.5,
            yanchor="middle",
            x=1.02,
            xanchor="left",
            font=dict(size=13, color="#475467"),
        ),
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_combinaciones_servicios_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos para combinaciones de servicios.")
        return

    df = df.copy()
    df["clientes"] = df["clientes"].fillna(0)
    df = df.sort_values("clientes", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["clientes"],
            y=df["CombinacionServicios"],
            orientation="h",
            text=[human_format(value) for value in df["clientes"]],
            textposition="outside",
            marker=dict(color="#0B74C8"),
            hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=True, gridcolor="#E8EEF5", zeroline=False, tickfont=dict(color="#7A869A")),
        yaxis=dict(title="", showgrid=False, automargin=True, tickfont=dict(size=12, color="#5B657A")),
        showlegend=False,
        bargap=0.22,
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_clientes_mayor_aporte_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos para clientes con mayor aporte.")
        return

    df = df.copy()
    df["AporteTotal"] = df["AporteTotal"].fillna(0)
    df = df.sort_values("AporteTotal", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["AporteTotal"],
            y=df["Cliente"],
            customdata=df[["ServiciosActivos"]],
            orientation="h",
            text=[human_format(value) for value in df["AporteTotal"]],
            textposition="outside",
            marker=dict(color="#C4D600"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Aporte total: %{x:,.2f}<br>"
                "Servicios: %{customdata[0]}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=True, gridcolor="#E8EEF5", zeroline=False, tickfont=dict(color="#7A869A")),
        yaxis=dict(title="", showgrid=False, automargin=True, tickfont=dict(size=12, color="#5B657A")),
        showlegend=False,
        bargap=0.22,
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_clasificacion_distribution_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos de clasificación integral.")
        return

    df = df.copy()
    df["clientes"] = df["clientes"].fillna(0)

    orden_deseado = [
        "Premium multiservicio",
        "Top en su servicio",
        "En desarrollo",
        "Oportunidad de expansión",
        "Pasivo multiservicio",
        "En riesgo",
        "Sin clasificación",
    ]

    categorias_presentes = [item for item in orden_deseado if item in df["ClasificacionIntegral"].tolist()]
    otras = [item for item in df["ClasificacionIntegral"].tolist() if item not in categorias_presentes]
    orden_final = categorias_presentes + otras

    df["ClasificacionIntegral"] = pd.Categorical(
        df["ClasificacionIntegral"],
        categories=orden_final,
        ordered=True,
    )
    df = df.sort_values("ClasificacionIntegral", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["clientes"],
            y=df["ClasificacionIntegral"],
            orientation="h",
            text=df["clientes"].apply(lambda value: f"{value:,.0f}".replace(",", ".")),
            textposition="outside",
            marker=dict(color="#C4D600"),
            hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#E8EEF5",
            zeroline=False,
            tickfont=dict(color="#7A869A"),
        ),
        yaxis=dict(title="", showgrid=False, tickfont=dict(size=13, color="#5B657A")),
        showlegend=False,
        bargap=0.22,
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_clasificacion_temporal_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos temporales de clasificación.")
        return

    color_map = {
        "Premium multiservicio": "#C4D600",
        "Top en su servicio": "#0B74C8",
        "En desarrollo": "#3B82F6",
        "Oportunidad de expansión": "#F59E0B",
        "Pasivo multiservicio": "#94A3B8",
        "En riesgo": "#EF4444",
        "Sin clasificación": "#CBD5E1",
    }

    fig = px.line(
        df,
        x="periodo",
        y="clientes",
        color="ClasificacionIntegral",
        markers=True,
        color_discrete_map=color_map,
    )

    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=False, tickfont=dict(color="#7A869A")),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#E8EEF5",
            zeroline=False,
            tickfont=dict(color="#7A869A"),
        ),
        legend=dict(orientation="h", y=-0.2, x=0, font=dict(size=11)),
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
