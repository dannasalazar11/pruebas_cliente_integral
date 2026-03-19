import streamlit as st

from features.buscador_clientes.models import CustomerSearchRequest


SEARCH_KEY = "buscador_clientes_request"
LOADING_KEY = "buscador_clientes_loading"


def initialize_state() -> None:
    if SEARCH_KEY not in st.session_state:
        st.session_state[SEARCH_KEY] = CustomerSearchRequest().to_payload()
    if LOADING_KEY not in st.session_state:
        st.session_state[LOADING_KEY] = False


def get_request() -> CustomerSearchRequest:
    initialize_state()
    return CustomerSearchRequest.from_payload(st.session_state.get(SEARCH_KEY))


def update_request(request: CustomerSearchRequest) -> None:
    st.session_state[SEARCH_KEY] = request.to_payload()


def set_loading(is_loading: bool) -> None:
    st.session_state[LOADING_KEY] = is_loading


def is_loading() -> bool:
    initialize_state()
    return bool(st.session_state.get(LOADING_KEY, False))
