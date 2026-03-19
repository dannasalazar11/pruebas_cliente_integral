from typing import Iterable

from repositories.dashboard_queries import get_dimension_service_columns, get_dimension_table

CLIENT_TABLE = "analiticaefg.clienteintegral.modelo_dimcliente"
CLIENT_CONTRACTS_TABLE = "analiticaefg.clienteintegral.modelo_datosclienteresidencial"
CLIENT_CONTRACTS_SUMMARY_TABLE = "analiticaefg.clienteintegral.modelo_contratosresidencial"
UBICACION_TABLE = "analiticaefg.clienteintegral.modelo_dimubicacion"
CONTRATO_TABLE = "dwhbiefg.comun.dimcontrato"

CATEGORY_MAPPING = {
    "Residencial": 1,
    "Comercial": 2,
}


def escape_sql_value(value: str) -> str:
    return value.replace("'", "''")


def get_tipo_identificacion_options_query() -> str:
    return f"""
    SELECT DISTINCT TipoIdentificacion
    FROM {CLIENT_CONTRACTS_TABLE}
    WHERE TipoIdentificacion IS NOT NULL
    ORDER BY TipoIdentificacion
    """


def get_cliente_raw_query(tipo_identificacion: str, identificacion: str) -> str:
    tipo_identificacion = escape_sql_value(tipo_identificacion)
    identificacion = escape_sql_value(identificacion)
    return f"""
    SELECT *
    FROM {CLIENT_TABLE}
    WHERE TipoIdentificacion = '{tipo_identificacion}'
      AND Identificacion = '{identificacion}'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY TipoIdentificacion, Identificacion
        ORDER BY TipoIdentificacion, Identificacion
    ) = 1
    """


def get_cliente_contratos_raw_query(tipo_identificacion: str, identificacion: str) -> str:
    tipo_identificacion = escape_sql_value(tipo_identificacion)
    identificacion = escape_sql_value(identificacion)
    return f"""
    SELECT *
    FROM {CLIENT_CONTRACTS_TABLE}
    WHERE TipoIdentificacion = '{tipo_identificacion}'
      AND Identificacion = '{identificacion}'
    """


def get_cliente_contratos_summary_query(tipo_identificacion: str, identificacion: str) -> str:
    tipo_identificacion = escape_sql_value(tipo_identificacion)
    identificacion = escape_sql_value(identificacion)
    return f"""
    SELECT TipoIdentificacion, Identificacion, contratos, ContratosActivos
    FROM {CLIENT_CONTRACTS_SUMMARY_TABLE}
    WHERE TipoIdentificacion = '{tipo_identificacion}'
      AND Identificacion = '{identificacion}'
    """


def _build_contract_in_clause(contracts: Iterable[str]) -> str:
    normalized = [str(contract).strip() for contract in contracts if str(contract).strip()]
    quoted = ", ".join([f"'{escape_sql_value(contract)}'" for contract in normalized])
    return f"c.Contrato IN ({quoted})"


def get_contratos_detalle_query(contracts: list[str], universo: str) -> str:
    if universo not in CATEGORY_MAPPING:
        raise ValueError(f"Universo no válido: {universo}")
    if not contracts:
        raise ValueError("La lista de contratos no puede estar vacía.")

    category = CATEGORY_MAPPING[universo]
    contract_filter = _build_contract_in_clause(contracts)

    return f"""
    SELECT
        c.Contrato,
        c.Estado,
        c.Categoria,
        c.Subcategoria,
        c.Direccion,
        u.barrio AS Barrio,
        u.localidad AS Localidad,
        u.departamento AS Departamento,
        u.mercado AS Mercado
    FROM {CONTRATO_TABLE} c
    LEFT JOIN {UBICACION_TABLE} u
      ON u.IdBarrio = c.Barrio
    WHERE c.Valido = 1
      AND c.Categoria = {category}
      AND {contract_filter}
    ORDER BY c.Contrato
    """


def get_cliente_dimensiones_query(tipo_identificacion: str, identificacion: str, universo: str) -> str:
    if universo not in CATEGORY_MAPPING:
        raise ValueError(f"Universo no válido: {universo}")

    tipo_identificacion = escape_sql_value(tipo_identificacion)
    identificacion = escape_sql_value(identificacion)
    dimension_table = get_dimension_table(universo)

    return f"""
    SELECT *
    FROM {dimension_table}
    WHERE TipoIdentificacion = '{tipo_identificacion}'
      AND Identificacion = '{identificacion}'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY TipoIdentificacion, Identificacion
        ORDER BY TipoIdentificacion, Identificacion
    ) = 1
    """


def get_cliente_detalle_servicio_query(
    tipo_identificacion: str,
    identificacion: str,
    universo: str,
    servicio: str,
    tipo_detalle: str,
) -> str:
    if tipo_detalle not in {"dimensiones", "indicadores", "variables"}:
        raise ValueError(f"Tipo de detalle inválido: {tipo_detalle}")

    valid_services = [column.lower() for column, _ in get_dimension_service_columns(universo)]
    if servicio.lower() not in valid_services:
        raise ValueError(f"Servicio inválido para {universo}: {servicio}")

    tipo_identificacion = escape_sql_value(tipo_identificacion)
    identificacion = escape_sql_value(identificacion)
    table_name = f"analiticaefg.clienteintegral.{servicio.lower()}_{universo.lower()}_consolidado_{tipo_detalle}"

    return f"""
    SELECT *
    FROM {table_name}
    WHERE TipoIdentificacion = '{tipo_identificacion}'
      AND Identificacion = '{identificacion}'
    """
