import pandas as pd
import streamlit as st

from features.valoracion_integral.models import DashboardFilters
from repositories.dashboard_queries import (
    get_clasificacion_integral_distribution_query,
    get_clasificacion_integral_query,
    get_clasificacion_integral_temporal_query,
    get_consolidado_general_query,
    get_detalle_servicio_query,
    get_filter_options_query,
    get_kpis_query,
    get_numero_servicios_query,
    get_penetracion_servicios_query,
)
from services.databricks_conn import run_query


def _filters_kwargs(filters: DashboardFilters) -> dict[str, list[str] | str]:
    return {
        "categoria": filters.categoria,
        "departamentos": list(filters.departamentos),
        "localidades": list(filters.localidades),
        "barrios": list(filters.barrios),
        "mercados": list(filters.mercados),
    }


@st.cache_data(ttl=3600)
def load_filter_options() -> pd.DataFrame:
    return run_query(get_filter_options_query())


@st.cache_data(ttl=300)
def load_kpis(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_kpis_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_penetracion_servicios(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_penetracion_servicios_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_numero_servicios(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_numero_servicios_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_clasificacion_integral(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_clasificacion_integral_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_clasificacion_integral_distribution(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_clasificacion_integral_distribution_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_clasificacion_integral_temporal(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_clasificacion_integral_temporal_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_consolidado_general(filters: DashboardFilters) -> pd.DataFrame:
    return run_query(get_consolidado_general_query(**_filters_kwargs(filters)))


@st.cache_data(ttl=300)
def load_detalle_servicio(
    filters: DashboardFilters,
    servicio: str,
    tipo_detalle: str,
) -> pd.DataFrame:
    return run_query(
        get_detalle_servicio_query(
            servicio=servicio,
            categoria=filters.categoria,
            tipo_detalle=tipo_detalle,
            departamentos=list(filters.departamentos),
            localidades=list(filters.localidades),
            barrios=list(filters.barrios),
            mercados=list(filters.mercados),
        )
    )
