import streamlit as st

from features.decisiones_estrategicas.models import (
    ConsolidarRequest,
    FidelizarRequest,
    PotenciarRequest,
    RecuperarRequest,
)


CONSOLIDAR_REQUEST_KEY = "decisiones_consolidar_request"
RECUPERAR_REQUEST_KEY = "decisiones_recuperar_request"
FIDELIZAR_REQUEST_KEY = "decisiones_fidelizar_request"
POTENCIAR_REQUEST_KEY = "decisiones_potenciar_request"


def initialize_state() -> None:
    if CONSOLIDAR_REQUEST_KEY not in st.session_state:
        st.session_state[CONSOLIDAR_REQUEST_KEY] = ConsolidarRequest().to_payload()
    if RECUPERAR_REQUEST_KEY not in st.session_state:
        st.session_state[RECUPERAR_REQUEST_KEY] = RecuperarRequest().to_payload()
    if FIDELIZAR_REQUEST_KEY not in st.session_state:
        st.session_state[FIDELIZAR_REQUEST_KEY] = FidelizarRequest().to_payload()
    if POTENCIAR_REQUEST_KEY not in st.session_state:
        st.session_state[POTENCIAR_REQUEST_KEY] = PotenciarRequest().to_payload()


def get_consolidar_request() -> ConsolidarRequest:
    initialize_state()
    return ConsolidarRequest.from_payload(st.session_state.get(CONSOLIDAR_REQUEST_KEY))


def update_consolidar_request(request: ConsolidarRequest) -> None:
    st.session_state[CONSOLIDAR_REQUEST_KEY] = request.to_payload()


def get_recuperar_request() -> RecuperarRequest:
    initialize_state()
    return RecuperarRequest.from_payload(st.session_state.get(RECUPERAR_REQUEST_KEY))


def update_recuperar_request(request: RecuperarRequest) -> None:
    st.session_state[RECUPERAR_REQUEST_KEY] = request.to_payload()


def get_fidelizar_request() -> FidelizarRequest:
    initialize_state()
    return FidelizarRequest.from_payload(st.session_state.get(FIDELIZAR_REQUEST_KEY))


def update_fidelizar_request(request: FidelizarRequest) -> None:
    st.session_state[FIDELIZAR_REQUEST_KEY] = request.to_payload()


def get_potenciar_request() -> PotenciarRequest:
    initialize_state()
    return PotenciarRequest.from_payload(st.session_state.get(POTENCIAR_REQUEST_KEY))


def update_potenciar_request(request: PotenciarRequest) -> None:
    st.session_state[POTENCIAR_REQUEST_KEY] = request.to_payload()
