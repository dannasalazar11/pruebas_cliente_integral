import re

import pandas as pd
import streamlit as st

from features.buscador_clientes.models import CustomerProfile, CustomerSearchRequest, CustomerSearchResult
from repositories.dashboard_queries import get_dimension_service_columns
from repositories.client_search_queries import (
    get_cliente_contratos_raw_query,
    get_cliente_detalle_servicio_query,
    get_cliente_dimensiones_query,
    get_cliente_raw_query,
    get_contratos_detalle_query,
    get_tipo_identificacion_options_query,
)
from services.databricks_conn import run_query


NAME_CANDIDATES = [
    "Nombre",
    "PrimerNombre",
    "Nombres",
    "NombreCliente",
    "nombre",
    "primer_nombre",
    "nombres",
]
LAST_NAME_CANDIDATES = [
    "Apellido",
    "PrimerApellido",
    "Apellidos",
    "ApellidoCliente",
    "apellido",
    "primer_apellido",
    "apellidos",
]
FULL_NAME_CANDIDATES = [
    "NombreCompleto",
    "NombreCompletoCliente",
    "nombre_completo",
    "nombrecompleto",
]
CONTRACT_COLUMN_CANDIDATES = ["Contrato", "Contratos", "contrato", "contratos"]
DETALLE_TIPOS = ("dimensiones", "indicadores", "variables")


def _normalize_column_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _find_first_matching_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized_candidates = {_normalize_column_name(candidate) for candidate in candidates}
    for column in df.columns:
        if _normalize_column_name(str(column)) in normalized_candidates:
            return str(column)
    return None


def _extract_name_parts(df: pd.DataFrame) -> tuple[str, str]:
    if df.empty:
        return "No disponible", "No disponible"

    row = df.iloc[0]
    name_column = _find_first_matching_column(df, NAME_CANDIDATES)
    last_name_column = _find_first_matching_column(df, LAST_NAME_CANDIDATES)

    nombre = str(row[name_column]).strip() if name_column and pd.notna(row[name_column]) else ""
    apellido = str(row[last_name_column]).strip() if last_name_column and pd.notna(row[last_name_column]) else ""

    if nombre or apellido:
        return nombre or "No disponible", apellido or "No disponible"

    full_name_column = _find_first_matching_column(df, FULL_NAME_CANDIDATES)
    if full_name_column and pd.notna(row[full_name_column]):
        full_name = str(row[full_name_column]).strip().split()
        if full_name:
            if len(full_name) == 1:
                return full_name[0], "No disponible"
            return full_name[0], " ".join(full_name[1:])

    return "No disponible", "No disponible"


def _extract_contracts(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []

    contract_column = _find_first_matching_column(df, CONTRACT_COLUMN_CANDIDATES)
    if not contract_column:
        return []

    contracts: list[str] = []
    for value in df[contract_column].dropna().tolist():
        if isinstance(value, str):
            parts = [part.strip() for part in re.split(r"[|,;]", value) if part.strip()]
            normalized_parts = [part.strip().strip("[]()'\"") for part in (parts or [value.strip()])]
            contracts.extend([part for part in normalized_parts if part])
        else:
            contracts.append(str(value).strip())

    seen: set[str] = set()
    unique_contracts: list[str] = []
    for contract in contracts:
        if contract and contract not in seen:
            seen.add(contract)
            unique_contracts.append(contract)
    return unique_contracts


def _get_active_services(dimensiones_df: pd.DataFrame, universo: str) -> tuple[str, ...]:
    if dimensiones_df.empty:
        return ()

    row = dimensiones_df.iloc[0]
    active_services: list[str] = []
    for column, label in get_dimension_service_columns(universo):
        matched_column = next(
            (current for current in dimensiones_df.columns if _normalize_column_name(str(current)) == _normalize_column_name(column)),
            None,
        )
        if matched_column is None:
            continue
        value = pd.to_numeric(pd.Series([row[matched_column]]), errors="coerce").fillna(0).iloc[0]
        if int(value) == 1:
            active_services.append(label)
    return tuple(active_services)


@st.cache_data(ttl=3600)
def load_tipo_identificacion_options() -> list[str]:
    df = run_query(get_tipo_identificacion_options_query())
    if df.empty:
        return []
    return sorted(df.iloc[:, 0].dropna().astype(str).unique().tolist())


@st.cache_data(ttl=300, show_spinner=False)
def load_cliente_raw(tipo_identificacion: str, identificacion: str) -> pd.DataFrame:
    return run_query(get_cliente_raw_query(tipo_identificacion, identificacion))


@st.cache_data(ttl=300, show_spinner=False)
def load_cliente_contratos_raw(tipo_identificacion: str, identificacion: str) -> pd.DataFrame:
    return run_query(get_cliente_contratos_raw_query(tipo_identificacion, identificacion))


@st.cache_data(ttl=300, show_spinner=False)
def load_contratos_detalle(contracts: tuple[str, ...], universo: str) -> pd.DataFrame:
    if not contracts:
        return pd.DataFrame()
    return run_query(get_contratos_detalle_query(list(contracts), universo))


@st.cache_data(ttl=300, show_spinner=False)
def load_cliente_dimensiones(tipo_identificacion: str, identificacion: str, universo: str) -> pd.DataFrame:
    return run_query(get_cliente_dimensiones_query(tipo_identificacion, identificacion, universo))


@st.cache_data(ttl=300, show_spinner=False)
def load_cliente_detalle_servicio(
    tipo_identificacion: str,
    identificacion: str,
    universo: str,
    servicio: str,
    tipo_detalle: str,
) -> pd.DataFrame:
    return run_query(
        get_cliente_detalle_servicio_query(
            tipo_identificacion=tipo_identificacion,
            identificacion=identificacion,
            universo=universo,
            servicio=servicio,
            tipo_detalle=tipo_detalle,
        )
    )


def search_customer(request: CustomerSearchRequest) -> CustomerSearchResult:
    cliente_raw = load_cliente_raw(request.tipo_identificacion, request.identificacion)
    if cliente_raw.empty:
        return CustomerSearchResult(
            profile=None,
            contratos=pd.DataFrame(),
            dimensiones=pd.DataFrame(),
            servicios_activos=(),
            detalle_servicios={},
        )

    nombre, apellido = _extract_name_parts(cliente_raw)
    contratos_raw = load_cliente_contratos_raw(request.tipo_identificacion, request.identificacion)
    contracts = _extract_contracts(contratos_raw)
    contratos_detalle = load_contratos_detalle(tuple(contracts), request.universo)
    dimensiones = load_cliente_dimensiones(request.tipo_identificacion, request.identificacion, request.universo)
    servicios_activos = _get_active_services(dimensiones, request.universo)
    detalle_servicios: dict[str, dict[str, pd.DataFrame]] = {}

    service_lookup = {label: column.lower() for column, label in get_dimension_service_columns(request.universo)}
    for servicio_label in servicios_activos:
        service_key = service_lookup.get(servicio_label)
        if not service_key:
            continue
        detalle_servicios[servicio_label] = {
            tipo: load_cliente_detalle_servicio(
                request.tipo_identificacion,
                request.identificacion,
                request.universo,
                service_key,
                tipo,
            )
            for tipo in DETALLE_TIPOS
        }

    profile = CustomerProfile(
        nombre=nombre,
        apellido=apellido,
        tipo_identificacion=request.tipo_identificacion,
        identificacion=request.identificacion,
    )
    return CustomerSearchResult(
        profile=profile,
        contratos=contratos_detalle,
        dimensiones=dimensiones,
        servicios_activos=servicios_activos,
        detalle_servicios=detalle_servicios,
    )
