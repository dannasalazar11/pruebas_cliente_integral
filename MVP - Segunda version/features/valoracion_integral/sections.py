import pandas as pd
import streamlit as st

from features.valoracion_integral.charts import (
    render_clasificacion_distribution_chart,
    render_clasificacion_temporal_chart,
    render_numero_servicios_chart,
    render_penetracion_servicios_chart,
)
from features.valoracion_integral.data import load_detalle_servicio
from features.valoracion_integral.formatters import format_millions, format_number
from features.valoracion_integral.models import DashboardFilters


def load_styles() -> None:
    st.markdown(
        """
        <style>
        .dashboard-title {
            font-size: 1.9rem;
            font-weight: 700;
            color: #1f3c88;
            margin-bottom: 0.25rem;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            color: #5e6e82;
            margin-bottom: 1.5rem;
        }

        div[data-testid="stForm"] {
            border: 1px solid #e7edf3;
            border-radius: 14px;
            padding: 14px 14px 6px 14px;
            background: #ffffff;
            margin-bottom: 1.2rem;
        }

        .kpi-card {
            border: 1px solid #e7edf3;
            border-radius: 14px;
            padding: 16px 18px;
            background: #ffffff;
            min-height: 130px;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
        }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }

        .kpi-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #334155;
            line-height: 1.3;
        }

        .kpi-icon {
            font-size: 1.1rem;
            color: #0b74c8;
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.1;
            margin-top: 8px;
        }

        .stMultiSelect div[data-baseweb="select"] > div,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 10px;
        }

        div[data-testid="stFormSubmitButton"] > button {
            background-color: #0b74c8 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 0.55rem 1rem !important;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #095c9d !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        '<div class="dashboard-title">Valoración Integral del Cliente</div>',
        unsafe_allow_html=True,
    )
    # st.markdown(
    #     '<div class="dashboard-subtitle">Resumen ejecutivo de clientes y contratos</div>',
    #     unsafe_allow_html=True,
    # )


def render_kpi_card(title: str, value: str, icon: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <div class="kpi-title">{title}</div>
                <div class="kpi-icon">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(df_kpis: pd.DataFrame) -> None:
    row = df_kpis.iloc[0]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card("Total de clientes", format_millions(row["TotalClientes"]), "👥")
    with col2:
        render_kpi_card("Total de contratos", format_millions(row["TotalContratos"]), "📄")
    with col3:
        render_kpi_card(
            "Promedio de servicios por cliente",
            format_number(row["PromedioServiciosPorCliente"], 2),
            "🧱",
        )
    with col4:
        render_kpi_card(
            "% de clientes con más de un servicio",
            f"{format_number(row['PorcentajeClientesMasDeUnServicio'], 1)}%",
            "☆",
        )


def render_penetracion_section(df_penetracion: pd.DataFrame, df_num_servicios: pd.DataFrame) -> None:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Clientes por servicio
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Cantidad de clientes con presencia en cada servicio")
            render_penetracion_servicios_chart(df_penetracion)

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Número de servicios por cliente
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Distribución de clientes según cantidad de servicios")
            render_numero_servicios_chart(df_num_servicios)


def render_clasificacion_section(df_distribution: pd.DataFrame, df_temporal: pd.DataFrame) -> None:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Distribución de clientes
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Clasificación integral de los clientes filtrados")
            render_clasificacion_distribution_chart(df_distribution)

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Marzo 2026
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Vista temporal provisional hasta contar con histórico mensual")
            render_clasificacion_temporal_chart(df_temporal)


def _format_consolidado_dataframe(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    servicio_extra_col = "SAD" if categoria == "Residencial" else "EfiSoluciones"
    df = df.rename(columns={"ServicioExtra": servicio_extra_col})

    for col in ["Consumo", "RTR", servicio_extra_col]:
        if col in df.columns:
            df[col] = df[col].apply(lambda value: "✓" if value == 1 else "✕")

    return df


def render_consolidado_section(
    df_consolidado: pd.DataFrame,
    filters: DashboardFilters,
) -> None:
    categoria = filters.categoria
    col1, col2 = st.columns([1, 1], gap="large")
    df_consolidado_fmt = _format_consolidado_dataframe(df_consolidado, categoria)

    with col1:
        with st.container(border=True):
            st.markdown("### Consolidado General")

            if df_consolidado_fmt.empty:
                st.info("No hay información consolidada para los filtros seleccionados.")
            else:
                st.dataframe(df_consolidado_fmt, width='stretch', height=420)
                st.download_button(
                    "Descargar CSV",
                    df_consolidado_fmt.to_csv(index=False).encode("utf-8"),
                    "consolidado_general.csv",
                    "text/csv",
                    key="download_consolidado_general",
                    on_click="ignore",
                )

    with col2:
        with st.container(border=True):
            st.markdown("### Detalle por Servicio")

            servicios = [
                ("consumo", "Consumo"),
                ("rtr", "RTR"),
                ("sad", "SAD") if categoria == "Residencial" else ("efisoluciones", "EfiSoluciones"),
            ]
            tipos = [
                ("Dimensiones", "dimensiones"),
                ("Indicadores", "indicadores"),
                ("Variables", "variables"),
            ]

            for servicio_tab, (servicio, servicio_label) in zip(st.tabs([label for _, label in servicios]), servicios):
                with servicio_tab:
                    for tipo_tab, (tipo_label, tipo_value) in zip(st.tabs([label for label, _ in tipos]), tipos):
                        with tipo_tab:
                            df_detalle = load_detalle_servicio(
                                filters=filters,
                                servicio=servicio,
                                tipo_detalle=tipo_value,
                            )

                            if df_detalle.empty:
                                st.info("No hay detalle disponible para esta combinación.")
                            else:
                                st.dataframe(df_detalle, width='stretch', height=380)
                                st.download_button(
                                    "Descargar CSV",
                                    df_detalle.to_csv(index=False).encode("utf-8"),
                                    f"{servicio}_{tipo_value}.csv",
                                    "text/csv",
                                    key=f"download_{categoria}_{servicio}_{tipo_value}",
                                    on_click="ignore",
                                )
