import streamlit as st


SERVICE_KEY = "info_selected_service"
DEFAULT_SERVICE = "Consumo"


def initialize_state() -> None:
    if SERVICE_KEY not in st.session_state:
        st.session_state[SERVICE_KEY] = DEFAULT_SERVICE


def get_selected_service() -> str:
    initialize_state()
    return str(st.session_state[SERVICE_KEY])


def set_selected_service(service_name: str) -> None:
    st.session_state[SERVICE_KEY] = service_name
