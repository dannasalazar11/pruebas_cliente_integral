import streamlit as st

from features.valoracion_integral.data import (
    load_consolidado_general,
    load_filter_options,
    load_kpis,
    load_numero_servicios,
    load_penetracion_servicios,
)
from features.valoracion_integral.filters import render_filters_form
from features.valoracion_integral.sections import (
    load_styles,
    render_consolidado_section,
    render_header,
    render_kpis,
    render_penetracion_section,
)
from features.valoracion_integral.state import get_filters, initialize_state, update_filters


def render() -> None:
    initialize_state()
    load_styles()
    render_header()

    current_filters = get_filters()
    df_options = load_filter_options()
    updated_filters = render_filters_form(df_options, current_filters)

    if updated_filters != current_filters:
        update_filters(updated_filters)

    filters = get_filters()
    df_kpis = load_kpis(filters)

    if df_kpis.empty:
        st.warning("No se encontraron datos para los filtros seleccionados.")
        return

    render_kpis(df_kpis)

    df_penetracion = load_penetracion_servicios(filters)
    df_num_servicios = load_numero_servicios(filters)
    render_penetracion_section(df_penetracion, df_num_servicios)

    df_consolidado = load_consolidado_general(filters)
    render_consolidado_section(df_consolidado, filters)
