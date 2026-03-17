from typing import Optional


TABLES = {
    "Residencial": {
        "clientes": "analiticaefg.clienteintegral.modelo_datosclienteresidencial",
        "servicio_extra_col": "sad",
    },
    "Comercial": {
        "clientes": "analiticaefg.clienteintegral.modelo_datosclientecomercial",
        "servicio_extra_col": "efisoluciones",
    },
}

DIMENSION_TABLES = {
    "Residencial": "analiticaefg.clienteintegral.dimensiones_residencial",
    "Comercial": "analiticaefg.clienteintegral.dimensiones_comercial",
}

MARKET_MAPPING = {
    "RISARALDA": "MERCADO RELEVANTE -ASE RISARALDA",
    "QUINDIO": "MERCADO RELEVANTE -ASE QUINDIO",
    "CALDAS": "MERCADO RELEVANTE -ASE CALDAS",
    "OCCIDENTE": "MERCADO RELEVANTE ASNE - MCIPIOS",
}

UBICACION_TABLE = "analiticaefg.clienteintegral.modelo_dimubicacion"


def escape_sql_value(value: str) -> str:
    return value.replace("'", "''")


def build_in_clause(column: str, values: Optional[list[str]]) -> str:
    if not values:
        return ""
    quoted = ", ".join([f"'{escape_sql_value(value)}'" for value in values])
    return f" AND {column} IN ({quoted}) "


def get_source_config(categoria: str) -> dict[str, str]:
    if categoria not in TABLES:
        raise ValueError(f"Categoría no válida: {categoria}")
    return TABLES[categoria]


def get_dimension_table(categoria: str) -> str:
    if categoria not in DIMENSION_TABLES:
        raise ValueError(f"Categoría no válida: {categoria}")
    return DIMENSION_TABLES[categoria]


def map_ui_markets_to_db_values(markets: Optional[list[str]]) -> list[str]:
    if not markets:
        return []
    return [MARKET_MAPPING.get(market, market) for market in markets]


def build_filters_where(
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    where = " WHERE 1=1 "
    where += build_in_clause("departamento", departamentos)
    where += build_in_clause("localidad", localidades)
    where += build_in_clause("barrio", barrios)
    where += build_in_clause("MercadoRelevante", map_ui_markets_to_db_values(mercados))
    return where


def get_filter_options_query() -> str:
    return f"""
        SELECT DISTINCT
            mercado,
            departamento,
            localidad,
            barrio
        FROM {UBICACION_TABLE}
        ORDER BY departamento, localidad, barrio
    """


def get_kpis_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)

    return f"""
    WITH base AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            Contrato,
            COALESCE(consumo, 0) AS consumo,
            COALESCE(rtr, 0) AS rtr,
            COALESCE({config['servicio_extra_col']}, 0) AS servicio_extra
        FROM {config['clientes']}
        {where_clause}
    ),
    clientes AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            MAX(consumo) + MAX(rtr) + MAX(servicio_extra) AS NumeroServicios
        FROM base
        GROUP BY TipoIdentificacion, Identificacion
    )
    SELECT
        (SELECT COUNT(*) FROM (
            SELECT DISTINCT TipoIdentificacion, Identificacion
            FROM base
        )) AS TotalClientes,
        (SELECT COUNT(DISTINCT Contrato) FROM base) AS TotalContratos,
        (SELECT AVG(NumeroServicios) FROM clientes) AS PromedioServiciosPorCliente,
        (
            SELECT 100.0 * SUM(CASE WHEN NumeroServicios > 1 THEN 1 ELSE 0 END) / COUNT(*)
            FROM clientes
        ) AS PorcentajeClientesMasDeUnServicio
    """


def get_penetracion_servicios_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    extra_service_label = "SAD" if categoria == "Residencial" else "EfiSoluciones"
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)

    return f"""
    WITH clientes AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            MAX(COALESCE(consumo, 0)) AS consumo,
            MAX(COALESCE(rtr, 0)) AS rtr,
            MAX(COALESCE({config['servicio_extra_col']}, 0)) AS servicio_extra
        FROM {config['clientes']}
        {where_clause}
        GROUP BY TipoIdentificacion, Identificacion
    )
    SELECT 'Consumo' AS servicio, SUM(consumo) AS clientes FROM clientes
    UNION ALL
    SELECT 'RTR' AS servicio, SUM(rtr) AS clientes FROM clientes
    UNION ALL
    SELECT '{extra_service_label}' AS servicio, SUM(servicio_extra) AS clientes FROM clientes
    """


def get_numero_servicios_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)

    return f"""
    WITH clientes AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            MAX(COALESCE(consumo, 0)) +
            MAX(COALESCE(rtr, 0)) +
            MAX(COALESCE({config['servicio_extra_col']}, 0)) AS NumeroServicios
        FROM {config['clientes']}
        {where_clause}
        GROUP BY TipoIdentificacion, Identificacion
    )
    SELECT
        NumeroServicios,
        COUNT(*) AS clientes,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS porcentaje
    FROM clientes
    GROUP BY NumeroServicios
    HAVING NumeroServicios > 0
    ORDER BY NumeroServicios
    """


def _build_clasificacion_base_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    dimension_table = get_dimension_table(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    return f"""
    WITH base_filtrada AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    clasif AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            ClasificacionIntegral
        FROM {dimension_table}
    )
    """


def get_clasificacion_integral_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    base_query = _build_clasificacion_base_query(categoria, departamentos, localidades, barrios, mercados)
    return base_query + """
    SELECT
        COALESCE(c.ClasificacionIntegral, 'Sin clasificación') AS ClasificacionIntegral,
        COUNT(*) AS clientes
    FROM base_filtrada b
    LEFT JOIN clasif c
        ON b.TipoIdentificacion = c.TipoIdentificacion
       AND b.Identificacion = c.Identificacion
    GROUP BY COALESCE(c.ClasificacionIntegral, 'Sin clasificación')
    ORDER BY clientes DESC
    """


def get_clasificacion_integral_distribution_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    return get_clasificacion_integral_query(categoria, departamentos, localidades, barrios, mercados)


def get_clasificacion_integral_temporal_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    base_query = _build_clasificacion_base_query(categoria, departamentos, localidades, barrios, mercados)
    return base_query + """
    SELECT
        'Marzo 2026' AS periodo,
        COALESCE(c.ClasificacionIntegral, 'Sin clasificación') AS ClasificacionIntegral,
        COUNT(*) AS clientes
    FROM base_filtrada b
    LEFT JOIN clasif c
        ON b.TipoIdentificacion = c.TipoIdentificacion
       AND b.Identificacion = c.Identificacion
    GROUP BY COALESCE(c.ClasificacionIntegral, 'Sin clasificación')
    ORDER BY ClasificacionIntegral
    """


CONSOLIDADO_DIM_TABLE = {
    "Residencial": "analiticaefg.clienteintegral.consumo_residencial_consolidado_dimensiones",
    "Comercial": "analiticaefg.clienteintegral.consumo_comercial_consolidado_dimensiones",
}

def get_consolidado_general_query(
    categoria,
    departamentos=None,
    localidades=None,
    barrios=None,
    mercados=None,
):
    config = get_source_config(categoria)
    base_table = config["clientes"]
    dimension_table = CONSOLIDADO_DIM_TABLE[categoria]

    where_clause = build_filters_where(
        departamentos=departamentos,
        localidades=localidades,
        barrios=barrios,
        mercados=mercados,
    )

    extra_service = config["servicio_extra_col"]

    return f"""
    WITH 
        clientes_filtrados as (
        SELECT distinct tipoidentificacion, identificacion
        from {base_table}
        {where_clause})

    SELECT 
        ref.TipoIdentificacion,
        ref.Identificacion,
        MAX(consumo) AS Consumo,
        MAX(rtr) AS RTR,
        MAX({extra_service}) AS ServicioExtra,
        dim.Economica,
        dim.Cumplimiento,
        dim.Relacional,
        dim.Potencial
    FROM {base_table} ref
    LEFT JOIN {dimension_table} dim
      ON ref.TipoIdentificacion = dim.TipoIdentificacion
     AND ref.Identificacion = dim.Identificacion
    INNER JOIN clientes_filtrados c
        on ref.tipoidentificacion=c.tipoidentificacion
        and ref.identificacion=c.identificacion
    GROUP BY
        ref.TipoIdentificacion,
        ref.Identificacion,
        dim.Economica,
        dim.Cumplimiento,
        dim.Relacional,
        dim.Potencial
    """

SERVICIOS_RESIDENCIAL = ["consumo", "rtr", "sad"]
SERVICIOS_COMERCIAL = ["consumo", "rtr", "efisoluciones"]

TIPOS_DETALLE = ["dimensiones", "indicadores", "variables"]


def get_detalle_servicio_query(
    servicio,
    categoria,
    tipo_detalle,
    departamentos=None,
    localidades=None,
    barrios=None,
    mercados=None,
):

    categoria_sql = categoria.lower()
    config = get_source_config(categoria)
    base_table = config["clientes"]
    where_clause = build_filters_where(
        departamentos=departamentos,
        localidades=localidades,
        barrios=barrios,
        mercados=mercados,
    )

    if categoria == "Residencial":
        if servicio not in SERVICIOS_RESIDENCIAL:
            raise ValueError("Servicio inválido para residencial")

    if categoria == "Comercial":
        if servicio not in SERVICIOS_COMERCIAL:
            raise ValueError("Servicio inválido para comercial")

    if tipo_detalle not in TIPOS_DETALLE:
        raise ValueError("Tipo de detalle inválido")

    table_name = f"analiticaefg.clienteintegral.{servicio}_{categoria_sql}_consolidado_{tipo_detalle}"

    return f"""
    WITH
        clientes_filtrados AS (
            SELECT DISTINCT
                TipoIdentificacion,
                Identificacion
            FROM {base_table}
            {where_clause}
        )
    SELECT detalle.*
    FROM {table_name} detalle
    INNER JOIN clientes_filtrados clientes
        ON detalle.TipoIdentificacion = clientes.TipoIdentificacion
       AND detalle.Identificacion = clientes.Identificacion
    """
