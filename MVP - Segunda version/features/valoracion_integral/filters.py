import pandas as pd
import streamlit as st

from features.valoracion_integral.models import DashboardFilters


MERCADOS_UI = ("CALDAS", "QUINDIO", "RISARALDA", "OCCIDENTE")
PERIODOS_DISPONIBLES = ("Marzo 2026",)
CATEGORIAS_DISPONIBLES = ("Residencial", "Comercial")


def get_dependent_options(
    df_options: pd.DataFrame,
    selected_departamentos: tuple[str, ...],
    selected_localidades: tuple[str, ...],
) -> tuple[list[str], list[str]]:
    df_filtered = df_options.copy()

    if selected_departamentos:
        df_filtered = df_filtered[df_filtered["departamento"].isin(selected_departamentos)]

    localidades = sorted(df_filtered["localidad"].dropna().unique().tolist())

    if selected_localidades:
        df_filtered = df_filtered[df_filtered["localidad"].isin(selected_localidades)]

    barrios = sorted(df_filtered["barrio"].dropna().unique().tolist())

    return localidades, barrios


def render_filters_form(
    df_options: pd.DataFrame,
    current_filters: DashboardFilters,
) -> DashboardFilters:
    departamentos_disponibles = sorted(df_options["departamento"].dropna().unique().tolist())

    with st.form("dashboard_filters_form"):
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            periodo = st.selectbox(
                "Periodo",
                options=list(PERIODOS_DISPONIBLES),
                index=PERIODOS_DISPONIBLES.index(current_filters.periodo),
            )

        with c2:
            categoria = st.selectbox(
                "Categoría",
                options=list(CATEGORIAS_DISPONIBLES),
                index=CATEGORIAS_DISPONIBLES.index(current_filters.categoria),
            )

        with c3:
            mercados = st.multiselect(
                "Mercados",
                options=list(MERCADOS_UI),
                default=list(current_filters.mercados),
            )

        with c4:
            departamentos = st.multiselect(
                "Departamentos",
                options=departamentos_disponibles,
                default=list(current_filters.departamentos),
            )

        with c5:
            localidades_disponibles, _ = get_dependent_options(
                df_options=df_options,
                selected_departamentos=tuple(departamentos),
                selected_localidades=(),
            )

            localidades = st.multiselect(
                "Localidades",
                options=localidades_disponibles,
                default=[item for item in current_filters.localidades if item in localidades_disponibles],
            )

        c6, c7, c8 = st.columns([2, 2, 1])

        with c6:
            _, barrios_disponibles = get_dependent_options(
                df_options=df_options,
                selected_departamentos=tuple(departamentos),
                selected_localidades=tuple(localidades),
            )

            barrios = st.multiselect(
                "Barrios",
                options=barrios_disponibles,
                default=[item for item in current_filters.barrios if item in barrios_disponibles],
            )

        with c7:
            st.write("")
            st.write("")
            aplicar = st.form_submit_button("Aplicar filtros")

        with c8:
            st.write("")

    if aplicar:
        return DashboardFilters(
            periodo=periodo,
            categoria=categoria,
            mercados=tuple(mercados),
            departamentos=tuple(departamentos),
            localidades=tuple(localidades),
            barrios=tuple(barrios),
        )

    return current_filters
