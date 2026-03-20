import re
from collections.abc import Iterable, Sequence

import pandas as pd
import streamlit as st

from features.decisiones_estrategicas.models import (
    ConsolidarRequest,
    FidelizarRequest,
    PotenciarRequest,
    RecuperarRequest,
)
from repositories.strategic_decisions_queries import (
    get_consolidado_variable_table,
    get_consolidar_query,
    get_fidelizar_query,
    get_potenciar_query,
    get_recuperar_query,
    get_service_options,
    get_table_columns_query,
)
from services.databricks_conn import run_query


EXCLUDED_KEY_COLUMNS = {"idcliente", "tipoidentificacion", "identificacion"}


def _normalize_column_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _format_date_list(value: object) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return value
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        formatted_items = []
        for item in value:
            if isinstance(item, pd.Timestamp):
                formatted_items.append(item.strftime("%Y-%m-%d"))
            else:
                text = str(item).strip()
                if text:
                    formatted_items.append(text)
        return ", ".join(formatted_items)
    return value


def _extract_contract_items_from_value(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned or cleaned in {"[]", "[ ]"}:
            return []
        return [token for token in re.findall(r"[A-Za-z0-9_-]+", cleaned) if token]
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


def count_contract_items(value: object) -> int:
    return len(_extract_contract_items_from_value(value))


@st.cache_data(ttl=3600)
def load_service_options(categoria: str) -> list[str]:
    return get_service_options(categoria)


@st.cache_data(ttl=3600)
def load_table_columns(table_name: str) -> list[str]:
    df_columns = run_query(get_table_columns_query(table_name))
    if df_columns.empty:
        return []
    column_name = df_columns.columns[0]
    return [
        str(value)
        for value in df_columns[column_name].tolist()
        if _normalize_column_name(str(value)) not in EXCLUDED_KEY_COLUMNS
    ]


def _build_variable_columns_map(request: ConsolidarRequest) -> dict[str, Sequence[str]]:
    columns_map: dict[str, Sequence[str]] = {}
    for servicio in request.servicios:
        table_name = get_consolidado_variable_table(servicio.lower(), request.categoria)
        columns_map[servicio] = load_table_columns(table_name)
    return columns_map


@st.cache_data(ttl=300, show_spinner=False)
def load_consolidar_result(request: ConsolidarRequest) -> pd.DataFrame:
    variable_columns = _build_variable_columns_map(request)
    df = run_query(
        get_consolidar_query(
            categoria=request.categoria,
            servicios=request.servicios,
            top_n=request.top_n,
            variable_columns_by_service=variable_columns,
        )
    )
    if df.empty:
        return df

    normalized_columns = {_normalize_column_name(str(column)): str(column) for column in df.columns}
    if "rtrfechasproximasrtr" in normalized_columns:
        column_name = normalized_columns["rtrfechasproximasrtr"]
        df[column_name] = df[column_name].apply(_format_date_list)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_recuperar_result(request: RecuperarRequest) -> pd.DataFrame:
    variable_columns: Sequence[str] = ()
    if request.servicio:
        table_name = get_consolidado_variable_table(request.servicio.lower(), request.categoria)
        variable_columns = load_table_columns(table_name)

    df = run_query(
        get_recuperar_query(
            categoria=request.categoria,
            servicio=request.servicio,
            top_n=request.top_n,
            variable_columns=variable_columns,
        )
    )
    if df.empty:
        return df

    normalized_columns = {_normalize_column_name(str(column)): str(column) for column in df.columns}
    if "rtrfechasproximasrtr" in normalized_columns:
        column_name = normalized_columns["rtrfechasproximasrtr"]
        df[column_name] = df[column_name].apply(_format_date_list)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_fidelizar_result(request: FidelizarRequest) -> pd.DataFrame:
    variable_columns_ancla: Sequence[str] = ()
    variable_columns_objetivo: Sequence[str] = ()

    if request.servicio_ancla:
        variable_columns_ancla = load_table_columns(
            get_consolidado_variable_table(request.servicio_ancla.lower(), request.categoria)
        )
    if request.servicio_objetivo:
        variable_columns_objetivo = load_table_columns(
            get_consolidado_variable_table(request.servicio_objetivo.lower(), request.categoria)
        )

    df = run_query(
        get_fidelizar_query(
            categoria=request.categoria,
            servicio_ancla=request.servicio_ancla,
            servicio_objetivo=request.servicio_objetivo,
            top_n=request.top_n,
            variable_columns_ancla=variable_columns_ancla,
            variable_columns_objetivo=variable_columns_objetivo,
        )
    )
    if df.empty:
        return df

    normalized_columns = {_normalize_column_name(str(column)): str(column) for column in df.columns}
    if "rtrfechasproximasrtr" in normalized_columns:
        column_name = normalized_columns["rtrfechasproximasrtr"]
        df[column_name] = df[column_name].apply(_format_date_list)
    return df


def _build_variable_columns_map_for_services(
    categoria: str,
    servicios: Sequence[str],
) -> dict[str, Sequence[str]]:
    columns_map: dict[str, Sequence[str]] = {}
    for servicio in servicios:
        table_name = get_consolidado_variable_table(servicio.lower(), categoria)
        columns_map[servicio] = load_table_columns(table_name)
    return columns_map


@st.cache_data(ttl=300, show_spinner=False)
def load_potenciar_result(request: PotenciarRequest) -> pd.DataFrame:
    variable_columns = _build_variable_columns_map_for_services(request.categoria, request.servicios)
    df = run_query(
        get_potenciar_query(
            categoria=request.categoria,
            servicios=request.servicios,
            top_n=request.top_n,
            variable_columns_by_service=variable_columns,
        )
    )
    if df.empty:
        return df

    normalized_columns = {_normalize_column_name(str(column)): str(column) for column in df.columns}
    if "rtrfechasproximasrtr" in normalized_columns:
        column_name = normalized_columns["rtrfechasproximasrtr"]
        df[column_name] = df[column_name].apply(_format_date_list)
    return df
