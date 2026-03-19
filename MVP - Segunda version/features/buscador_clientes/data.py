import re
from collections.abc import Iterable

import pandas as pd
import streamlit as st

from features.buscador_clientes.models import CustomerProfile, CustomerSearchRequest, CustomerSearchResult
from repositories.dashboard_queries import get_dimension_service_columns
from repositories.client_search_queries import (
    get_cliente_contratos_raw_query,
    get_cliente_contratos_summary_query,
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
ACTIVE_CONTRACT_COLUMN_CANDIDATES = ["ContratosActivos", "contratosactivos", "contratos_activos"]
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
        contracts.extend(_extract_contract_items_from_value(value))

    seen: set[str] = set()
    unique_contracts: list[str] = []
    for contract in contracts:
        if contract and contract not in seen:
            seen.add(contract)
            unique_contracts.append(contract)
    return unique_contracts


def _extract_contract_items_from_value(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        cleaned_value = value.strip()
        if not cleaned_value or cleaned_value in {"[]", "[ ]"}:
            return []
        # Soporta listas tipo "[1,2]", "[1 2]" o formatos similares.
        return [token for token in re.findall(r"[A-Za-z0-9_-]+", cleaned_value) if token]

    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        items: list[str] = []
        for item in value:
            items.extend(_extract_contract_items_from_value(item))
        return items

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            return _extract_contract_items_from_value(value.tolist())
        except Exception:
            pass

    text_value = str(value).strip()
    return [text_value] if text_value else []


def _count_contract_list_items(df: pd.DataFrame, column_candidates: list[str]) -> int:
    if df.empty:
        return 0

    contract_column = _find_first_matching_column(df, column_candidates)
    if not contract_column:
        return 0

    total_items = 0
    for value in df[contract_column].dropna().tolist():
        total_items += len(_extract_contract_items_from_value(value))
    return total_items


def _extract_contract_summary(df: pd.DataFrame) -> tuple[int, int]:
    if df.empty:
        return 0, 0

    total_contracts = _count_contract_list_items(df, CONTRACT_COLUMN_CANDIDATES)
    active_contracts = _count_contract_list_items(df, ACTIVE_CONTRACT_COLUMN_CANDIDATES)
    return total_contracts, active_contracts


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
def load_cliente_contratos_summary_raw(tipo_identificacion: str, identificacion: str) -> pd.DataFrame:
    return run_query(get_cliente_contratos_summary_query(tipo_identificacion, identificacion))


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


def load_customer_profile(request: CustomerSearchRequest) -> CustomerProfile | None:
    cliente_raw = load_cliente_raw(request.tipo_identificacion, request.identificacion)
    if cliente_raw.empty:
        return None

    nombre, apellido = _extract_name_parts(cliente_raw)
    return CustomerProfile(
        nombre=nombre,
        apellido=apellido,
        tipo_identificacion=request.tipo_identificacion,
        identificacion=request.identificacion,
    )


def load_customer_integral(request: CustomerSearchRequest) -> tuple[pd.DataFrame, tuple[str, ...]]:
    dimensiones = load_cliente_dimensiones(request.tipo_identificacion, request.identificacion, request.universo)
    servicios_activos = _get_active_services(dimensiones, request.universo)
    return dimensiones, servicios_activos


def load_customer_service_details(
    request: CustomerSearchRequest,
    servicios_activos: tuple[str, ...],
) -> dict[str, dict[str, pd.DataFrame]]:
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

    return detalle_servicios


def load_customer_contracts(request: CustomerSearchRequest) -> pd.DataFrame:
    contratos_raw = load_cliente_contratos_raw(request.tipo_identificacion, request.identificacion)
    contracts = _extract_contracts(contratos_raw)
    return load_contratos_detalle(tuple(contracts), request.universo)


def load_customer_contracts_summary(request: CustomerSearchRequest) -> tuple[int, int]:
    contratos_summary_raw = load_cliente_contratos_summary_raw(request.tipo_identificacion, request.identificacion)
    return _extract_contract_summary(contratos_summary_raw)
