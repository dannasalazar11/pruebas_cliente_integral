import pandas as pd
import streamlit as st
import unicodedata

from features.valoracion_integral.charts import (
    render_clientes_mayor_aporte_chart,
    render_clasificacion_distribution_chart,
    render_clasificacion_temporal_chart,
    render_combinaciones_servicios_chart,
    render_numero_servicios_chart,
    render_penetracion_servicios_chart,
    render_service_classification_chart,
)
from features.valoracion_integral.data import (
    TABLE_PREVIEW_LIMIT,
    load_consolidado_general,
    load_detalle_servicio,
    load_service_classification,
    load_service_classification_profile,
)
from features.valoracion_integral.formatters import format_millions, format_number
from features.valoracion_integral.models import DashboardFilters


CONSOLIDADO_SERVICE_LABELS = {
    "Residencial": {
        "consumo": "Consumo",
        "rtr": "RTR",
        "sad": "SAD",
        "seguros": "Seguros",
        "brilla": "Brilla",
    },
    "Comercial": {
        "consumo": "Consumo",
        "rtr": "RTR",
        "efisoluciones": "Efisoluciones",
        "brilla": "Brilla",
    },
}

CONSOLIDADO_SECTION_HEIGHT = 700


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
        render_kpi_card("Total de clientes", format_millions(row["TotalClientes"]), "👤")
    with col2:
        render_kpi_card("Total de contratos", format_millions(row["TotalContratos"]), "📄")
    with col3:
        render_kpi_card(
            "Promedio de servicios por cliente",
            format_number(row["PromedioServiciosPorCliente"], 2),
            "🔗",
        )
    with col4:
        render_kpi_card(
            "% de clientes con 3 o más servicios",
            f"{format_number(row['PorcentajeClientesTresOMasServicios'], 1)}%",
            "📊",
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


def render_nuevos_indicadores_section(
    df_combinaciones: pd.DataFrame,
    df_aporte: pd.DataFrame,
) -> None:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Combinaciones más usuales de servicios
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Ranking de las combinaciones de servicios más frecuentes en los clientes filtrados")
            render_combinaciones_servicios_chart(df_combinaciones)

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                    Clientes con mayor aporte
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Clientes con mayor aporte total y servicios activos asociados")
            render_clientes_mayor_aporte_chart(df_aporte)


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


def render_service_classification_section(filters: DashboardFilters) -> None:
    categoria = filters.categoria
    if categoria == "Residencial":
        servicios = [
            ("consumo", "Consumo"),
            ("rtr", "RTR"),
            ("sad", "SAD"),
            ("brilla", "Brilla"),
            ("seguros", "Seguros"),
        ]
    else:
        servicios = [
            ("consumo", "Consumo"),
            ("rtr", "RTR"),
            ("efisoluciones", "Efisoluciones"),
            ("brilla", "Brilla"),
        ]

    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size:1.2rem;font-weight:700;color:#1f3c88;margin:0 0 0.8rem 0;">
                CLASIFICACIÓN POR SERVICIO
            </div>
            """,
            unsafe_allow_html=True,
        )

        for service_tab, (servicio, servicio_label) in zip(st.tabs([label for _, label in servicios]), servicios):
            with service_tab:
                if servicio != "brilla":
                    st.info(f"Aún no hay clasificación disponible para {servicio_label}.")
                    continue

                df_clasificacion = load_service_classification(filters, servicio)
                total_clientes = int(df_clasificacion["clientes"].sum()) if not df_clasificacion.empty else 0
                df_profile = load_service_classification_profile(filters, servicio)

                col1, col2 = st.columns([1.55, 1], gap="large")

                with col1:
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                                Distribución - <span style="color:#0B74C8;">{servicio_label}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.caption("Clasificación RFM de los clientes filtrados dentro del servicio")
                        summary_col, _ = st.columns([0.52, 0.48], gap="medium")
                        with summary_col:
                            st.markdown(
                                f"""
                                <div class="search-summary-card" style="margin-bottom:0.5rem;">
                                    <div class="search-summary-label">Total clientes del servicio</div>
                                    <div class="search-summary-value" style="font-size:1.9rem;">{format_millions(total_clientes)}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        render_service_classification_chart(df_clasificacion)

                with col2:
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style="font-size:1.05rem;font-weight:700;color:#334155;margin-bottom:0.2rem;">
                                Perfil promedio - <span style="color:#0B74C8;">{servicio_label}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.caption("Promedio de las dimensiones de los clientes en este servicio")
                        _render_service_profile_average(df_profile)


def _render_summary_metric_card(title: str, value: object) -> None:
    st.markdown(
        f"""
        <div style="border:1px solid #e7edf3;border-radius:14px;padding:16px 18px;background:#ffffff;margin-bottom:0.85rem;">
            <div style="font-size:0.82rem;text-transform:uppercase;letter-spacing:0.04em;color:#7a869a;margin-bottom:0.3rem;">
                {title}
            </div>
            <div style="font-size:1.55rem;font-weight:700;color:#0f172a;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_profile_progress_row(label: str, value: float, color: str, icon: str) -> None:
    percentage = max(0.0, min(100.0, value * 100.0))
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin:0.55rem 0 0.25rem 0;">
            <div style="font-size:0.98rem;font-weight:600;color:#334155;">{icon} {label}</div>
            <div style="font-size:0.98rem;font-weight:700;color:#0f172a;">{percentage:.0f}</div>
        </div>
        <div style="width:100%;height:10px;border-radius:999px;background:#e5e7eb;overflow:hidden;margin-bottom:0.85rem;">
            <div style="width:{percentage:.1f}%;height:100%;border-radius:999px;background:{color};"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_service_profile_average(df_profile: pd.DataFrame) -> None:
    if df_profile.empty:
        st.info("No hay perfil promedio disponible para este servicio.")
        return

    row = df_profile.iloc[0].fillna(0)
    score_promedio = (
        float(row.get("Economica", 0))
        + float(row.get("Cumplimiento", 0))
        + float(row.get("Relacional", 0))
        + float(row.get("Potencial", 0))
    ) / 4.0

    st.markdown(
        f"""
        <div style="border:1px solid #dbeafe;border-radius:16px;padding:16px 18px;background:linear-gradient(90deg,#eef5ff 0%,#ffffff 100%);margin-bottom:1rem;">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:68px;height:68px;border-radius:50%;background:#2563eb;color:#ffffff;display:flex;align-items:center;justify-content:center;font-size:1.7rem;font-weight:700;">◔</div>
                <div>
                    <div style="font-size:0.98rem;color:#475467;margin-bottom:0.2rem;">Score promedio</div>
                    <div style="font-size:2.15rem;font-weight:800;color:#0f172a;line-height:1;">{score_promedio * 100:.0f}<span style="font-size:1.1rem;color:#64748b;font-weight:700;">/100</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_profile_progress_row("Económica", float(row.get("Economica", 0)), "#16a34a", "💲")
    _render_profile_progress_row("Cumplimiento", float(row.get("Cumplimiento", 0)), "#2563eb", "✅")
    _render_profile_progress_row("Relacional", float(row.get("Relacional", 0)), "#9333ea", "👥")
    _render_profile_progress_row("Potencial", float(row.get("Potencial", 0)), "#f97316", "🎯")


def _normalize_column_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _rename_columns_by_normalized_name(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    normalized_map = {_normalize_column_name(source): target for source, target in rename_map.items()}
    return df.rename(
        columns={
            column: normalized_map.get(_normalize_column_name(column), column)
            for column in df.columns
        }
    )


def _prepare_consolidado_download_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df.columns = [
        "".join(
            char
            for char in unicodedata.normalize("NFKD", str(column))
            if not unicodedata.combining(char)
        )
        for column in df.columns
    ]
    for column in df.columns:
        if _normalize_column_name(str(column)) == "tipoidentificacion":
            df[column] = df[column].apply(
                lambda value: "".join(
                    char
                    for char in unicodedata.normalize("NFKD", value)
                    if not unicodedata.combining(char)
                )
                if isinstance(value, str)
                else value
            )
    return df


def _format_consolidado_dataframe(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df = _rename_columns_by_normalized_name(
        df,
        {
            "tipoidentificacion": "TipoIdentificacion",
            "identificacion": "Identificacion",
            **CONSOLIDADO_SERVICE_LABELS[categoria],
        },
    )

    for col in CONSOLIDADO_SERVICE_LABELS[categoria].values():
        if col in df.columns:
            numeric_values = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            df[col] = numeric_values.apply(lambda value: "✅" if value == 1 else "❌")

    return df


def _get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["number"]).columns.tolist()


def _get_zero_to_one_columns(df: pd.DataFrame, excluded_columns: list[str] | None = None) -> list[str]:
    excluded = set(excluded_columns or [])
    valid_columns: list[str] = []

    for column in _get_numeric_columns(df):
        if column in excluded:
            continue
        values = df[column].dropna()
        if values.empty:
            continue
        if ((values >= 0) & (values <= 1)).all():
            valid_columns.append(column)

    return valid_columns


def _style_consolidado_dataframe(df: pd.DataFrame, categoria: str):
    service_columns = [
        column for column in CONSOLIDADO_SERVICE_LABELS[categoria].values() if column in df.columns
    ]
    numeric_columns = [column for column in _get_numeric_columns(df) if column not in service_columns]

    def service_cell_style(value: object) -> str:
        if value == "✅":
            return "background-color: #e8f7ee; color: #166534; font-weight: 600; text-align: center;"
        if value == "❌":
            return "background-color: #fdecec; color: #b42318; font-weight: 600; text-align: center;"
        return ""

    styled = df.style
    if service_columns:
        styled = styled.map(service_cell_style, subset=service_columns)
    if numeric_columns:
        styled = styled.format("{:.2f}", subset=numeric_columns)

    return styled.set_properties(
        **{
            "border-color": "#e7edf3",
            "font-size": "0.92rem",
        }
    )


def _style_detalle_dataframe(df: pd.DataFrame, tipo_detalle: str):
    excluded_columns = [
        column
        for column in df.columns
        if _normalize_column_name(str(column)) in {"tipoidentificacion", "identificacion"}
    ]
    numeric_columns = _get_numeric_columns(df)
    styled = df.style
    if numeric_columns:
        styled = styled.format("{:.2f}", subset=numeric_columns)

    return styled.set_properties(
        **{
            "border-color": "#e7edf3",
            "font-size": "0.92rem",
        }
    )


@st.fragment
def _render_lazy_download_button(
    *,
    button_label: str,
    download_label: str,
    cache_key: str,
    file_name: str,
    query_loader,
    formatter,
) -> None:
    if st.button(button_label, key=f"{cache_key}_prepare"):
        with st.spinner("Consultando la tabla completa para descarga..."):
            st.session_state[cache_key] = formatter(query_loader())

    cached_df = st.session_state.get(cache_key)
    if cached_df is not None:
        st.download_button(
            download_label,
            cached_df.to_csv(index=False).encode("utf-8"),
            file_name,
            "text/csv",
            key=f"{cache_key}_download",
            on_click="ignore",
        )


def render_consolidado_section(
    df_consolidado: pd.DataFrame,
    filters: DashboardFilters,
) -> None:
    categoria = filters.categoria
    col1, col2 = st.columns([1, 1], gap="large")
    df_consolidado_fmt = _format_consolidado_dataframe(df_consolidado, categoria)

    with col1:
        with st.container(border=True, height=CONSOLIDADO_SECTION_HEIGHT):
            st.markdown("### Consolidado General")

            if df_consolidado_fmt.empty:
                st.info("No hay información consolidada para los filtros seleccionados.")
            else:
                st.caption(f"Mostrando top {TABLE_PREVIEW_LIMIT} registros para cuidar memoria.")
                st.dataframe(
                    _style_consolidado_dataframe(df_consolidado_fmt, categoria),
                    width='stretch',
                    height=420,
                )
                _render_lazy_download_button(
                    button_label="Preparar descarga completa",
                    download_label="Descargar CSV completo",
                    cache_key=f"consolidado_full_{categoria}_{hash(filters)}",
                    file_name="consolidado_general.csv",
                    query_loader=lambda: load_consolidado_general(filters, limit=None),
                    formatter=_prepare_consolidado_download_dataframe,
                )

    with col2:
        with st.container(border=True, height=CONSOLIDADO_SECTION_HEIGHT):
            st.markdown("### Detalle por Servicio")

            if categoria == "Residencial":
                servicios = [
                    ("consumo", "Consumo"),
                    ("rtr", "RTR"),
                    ("sad", "SAD"),
                    ("seguros", "Seguros"),
                    ("brilla", "Brilla"),
                ]
            else:
                servicios = [
                    ("consumo", "Consumo"),
                    ("rtr", "RTR"),
                    ("efisoluciones", "Efisoluciones"),
                    ("brilla", "Brilla"),
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
                                st.caption(f"Mostrando top {TABLE_PREVIEW_LIMIT} registros para cuidar memoria.")
                                st.dataframe(
                                    _style_detalle_dataframe(df_detalle, tipo_value),
                                    width='stretch',
                                    height=380,
                                )
                                _render_lazy_download_button(
                                    button_label="Preparar descarga completa",
                                    download_label="Descargar CSV completo",
                                    cache_key=(
                                        f"detalle_full_{categoria}_{servicio}_{tipo_value}_{hash(filters)}"
                                    ),
                                    file_name=f"{servicio}_{tipo_value}.csv",
                                    query_loader=lambda s=servicio, t=tipo_value: load_detalle_servicio(
                                        filters=filters,
                                        servicio=s,
                                        tipo_detalle=t,
                                        limit=None,
                                    ),
                                    formatter=lambda df: df,
                                )
