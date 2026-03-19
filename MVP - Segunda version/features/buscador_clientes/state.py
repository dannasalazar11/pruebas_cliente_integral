import streamlit as st

from features.buscador_clientes.models import CustomerSearchRequest


SEARCH_KEY = "buscador_clientes_request"


def initialize_state() -> None:
    if SEARCH_KEY not in st.session_state:
        st.session_state[SEARCH_KEY] = CustomerSearchRequest().to_payload()


def get_request() -> CustomerSearchRequest:
    initialize_state()
    return CustomerSearchRequest.from_payload(st.session_state.get(SEARCH_KEY))


def update_request(request: CustomerSearchRequest) -> None:
    st.session_state[SEARCH_KEY] = request.to_payload()
