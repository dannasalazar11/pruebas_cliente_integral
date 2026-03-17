import streamlit as st

from features.valoracion_integral.models import DashboardFilters


FILTERS_KEY = "dashboard_filters_applied"


def initialize_state() -> None:
    if FILTERS_KEY not in st.session_state:
        st.session_state[FILTERS_KEY] = DashboardFilters().to_payload()


def get_filters() -> DashboardFilters:
    initialize_state()
    return DashboardFilters.from_payload(st.session_state.get(FILTERS_KEY))


def update_filters(filters: DashboardFilters) -> None:
    st.session_state[FILTERS_KEY] = filters.to_payload()
