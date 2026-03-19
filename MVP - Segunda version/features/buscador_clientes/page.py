import streamlit as st

from features.buscador_clientes.data import (
    load_customer_contracts,
    load_customer_contracts_summary,
    load_customer_integral,
    load_customer_profile,
    load_customer_service_details,
    load_tipo_identificacion_options,
)
from features.buscador_clientes.sections_clean import (
    render_customer_integral_overview,
    load_styles,
    render_contracts_details,
    render_contracts_summary,
    render_customer_profile,
    render_header,
    render_search_form,
    render_service_details_dashboard,
)
from features.buscador_clientes.state import get_request, initialize_state, is_loading, set_loading, update_request


def render() -> None:
    initialize_state()
    load_styles()
    render_header()

    current_request = get_request()
    tipo_identificacion_options = load_tipo_identificacion_options()
    if not tipo_identificacion_options:
        st.warning("No fue posible cargar el catálogo de tipos de identificación.")
        return

    updated_request = render_search_form(tipo_identificacion_options, current_request)

    if updated_request is not None:
        if not updated_request.tipo_identificacion or not updated_request.identificacion:
            st.warning("Selecciona el tipo de identificación y escribe un número de identificación para buscar.")
            return
        update_request(updated_request)
        set_loading(True)
        st.rerun()
        current_request = updated_request

    if not current_request.searched:
        st.info("Selecciona el universo, el tipo de identificación y busca un cliente para ver su información.")
        return

    profile_slot = st.empty()
    integral_slot = st.empty()
    details_slot = st.empty()
    contracts_summary_slot = st.empty()
    contracts_detail_slot = st.empty()

    if is_loading():
        with profile_slot.container():
            st.info("Preparando una nueva búsqueda...")

    with profile_slot.container():
        with st.spinner("Cargando información del cliente..."):
            profile = load_customer_profile(current_request)

        if profile is None:
            st.warning("No se encontró un cliente con el tipo y número de identificación ingresados.")
            return

        render_customer_profile(profile)

    with integral_slot.container():
        with st.spinner("Cargando perfil integral y servicios activos..."):
            dimensiones, servicios_activos = load_customer_integral(current_request)
        render_customer_integral_overview(dimensiones, servicios_activos)

    with details_slot.container():
        with st.spinner("Cargando detalle por servicio..."):
            detalle_servicios = load_customer_service_details(current_request, servicios_activos)
        render_service_details_dashboard(detalle_servicios)

    with contracts_summary_slot.container():
        with st.spinner("Cargando contratos..."):
            total_contracts, active_contracts = load_customer_contracts_summary(current_request)
        render_contracts_summary(total_contracts, active_contracts)

    with contracts_detail_slot.container():
        with st.spinner("Cargando detalle de contratos..."):
            contratos = load_customer_contracts(current_request)
            render_contracts_details(contratos)

    set_loading(False)
