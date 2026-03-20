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

DIMENSION_SERVICE_COLUMNS = {
    "Residencial": [
        ("consumo", "Consumo"),
        ("rtr", "RTR"),
        ("sad", "SAD"),
        ("Brilla", "Brilla"),
        ("seguros", "Seguros"),
    ],
    "Comercial": [
        ("consumo", "Consumo"),
        ("rtr", "RTR"),
        ("efisoluciones", "Efisoluciones"),
        ("brilla", "Brilla"),
    ],
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


def build_limit_clause(limit: Optional[int] = None) -> str:
    if limit is None:
        return ""
    if limit <= 0:
        raise ValueError("El límite debe ser mayor que cero.")
    return f"\n    LIMIT {limit}"


def get_source_config(categoria: str) -> dict[str, str]:
    if categoria not in TABLES:
        raise ValueError(f"Categoría no válida: {categoria}")
    return TABLES[categoria]


def get_dimension_table(categoria: str) -> str:
    if categoria not in DIMENSION_TABLES:
        raise ValueError(f"Categoría no válida: {categoria}")
    return DIMENSION_TABLES[categoria]


def get_dimension_service_columns(categoria: str) -> list[tuple[str, str]]:
    if categoria not in DIMENSION_SERVICE_COLUMNS:
        raise ValueError(f"Categoría no válida: {categoria}")
    return DIMENSION_SERVICE_COLUMNS[categoria]


def get_variable_table_name(servicio: str, categoria: str) -> str:
    return f"analiticaefg.clienteintegral.{servicio}_{categoria.lower()}_consolidado_variables"


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
    dimension_table = get_dimension_table(categoria)
    service_columns = get_dimension_service_columns(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    numero_servicios_expr = " +\n            ".join(
        [f"COALESCE(dim.{column}, 0)" for column, _ in service_columns]
    )

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    clientes_dim AS (
        SELECT
            dim.TipoIdentificacion,
            dim.Identificacion,
            {numero_servicios_expr} AS NumeroServicios
        FROM {dimension_table} dim
        INNER JOIN clientes_filtrados clientes
            ON dim.TipoIdentificacion = clientes.TipoIdentificacion
           AND dim.Identificacion = clientes.Identificacion
    ),
    contratos AS (
        SELECT DISTINCT
            ref.Contrato
        FROM {config['clientes']} ref
        INNER JOIN clientes_dim clientes
            ON ref.TipoIdentificacion = clientes.TipoIdentificacion
           AND ref.Identificacion = clientes.Identificacion
    )
    SELECT
        (SELECT COUNT(*) FROM clientes_dim) AS TotalClientes,
        (SELECT COUNT(*) FROM contratos) AS TotalContratos,
        (SELECT AVG(NumeroServicios) FROM clientes_dim) AS PromedioServiciosPorCliente,
        (
            SELECT 100.0 * SUM(CASE WHEN NumeroServicios >= 3 THEN 1 ELSE 0 END) / COUNT(*)
            FROM clientes_dim
        ) AS PorcentajeClientesTresOMasServicios
    """


def get_penetracion_servicios_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    dimension_table = get_dimension_table(categoria)
    service_columns = get_dimension_service_columns(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    cte_columns = ",\n            ".join(
        [f"COALESCE(dim.{column}, 0) AS {column}" for column, _ in service_columns]
    )
    union_queries = "\n    UNION ALL\n".join(
        [
            f"SELECT '{label}' AS servicio, SUM({column}) AS clientes FROM clientes"
            for column, label in service_columns
        ]
    )

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    clientes AS (
        SELECT
            dim.TipoIdentificacion,
            dim.Identificacion,
            {cte_columns}
        FROM {dimension_table} dim
        INNER JOIN clientes_filtrados clientes
            ON dim.TipoIdentificacion = clientes.TipoIdentificacion
           AND dim.Identificacion = clientes.Identificacion
    )
    {union_queries}
    """


def get_numero_servicios_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    dimension_table = get_dimension_table(categoria)
    service_columns = get_dimension_service_columns(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    numero_servicios_expr = " +\n                ".join(
        [f"COALESCE(dim.{column}, 0)" for column, _ in service_columns]
    )
    max_servicios = len(service_columns)

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    clientes AS (
        SELECT
            dim.TipoIdentificacion,
            dim.Identificacion,
            {numero_servicios_expr} AS NumeroServicios
        FROM {dimension_table} dim
        INNER JOIN clientes_filtrados clientes
            ON dim.TipoIdentificacion = clientes.TipoIdentificacion
           AND dim.Identificacion = clientes.Identificacion
    )
    SELECT
        NumeroServicios,
        COUNT(*) AS clientes,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS porcentaje
    FROM clientes
    GROUP BY NumeroServicios
    HAVING NumeroServicios BETWEEN 1 AND {max_servicios}
    ORDER BY NumeroServicios
    """


def _build_service_combination_expr(service_columns: list[tuple[str, str]]) -> str:
    service_cases = ",\n                ".join(
        [f"CASE WHEN COALESCE(dim.{column}, 0) = 1 THEN '{label}' END" for column, label in service_columns]
    )
    return f"CONCAT_WS(' + ',\n                {service_cases}\n            )"


def get_combinaciones_servicios_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    dimension_table = get_dimension_table(categoria)
    service_columns = get_dimension_service_columns(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    numero_servicios_expr = " +\n                ".join(
        [f"COALESCE(dim.{column}, 0)" for column, _ in service_columns]
    )
    combinacion_expr = _build_service_combination_expr(service_columns)

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    clientes_dim AS (
        SELECT
            dim.TipoIdentificacion,
            dim.Identificacion,
            {numero_servicios_expr} AS NumeroServicios,
            {combinacion_expr} AS CombinacionServicios
        FROM {dimension_table} dim
        INNER JOIN clientes_filtrados clientes
            ON dim.TipoIdentificacion = clientes.TipoIdentificacion
           AND dim.Identificacion = clientes.Identificacion
    )
    SELECT
        CombinacionServicios,
        COUNT(*) AS clientes
    FROM clientes_dim
    WHERE NumeroServicios > 0
    GROUP BY CombinacionServicios
    ORDER BY clientes DESC, CombinacionServicios
    LIMIT 5
    """


def get_clientes_mayor_aporte_query(
    categoria: str,
    departamentos: Optional[list[str]] = None,
    localidades: Optional[list[str]] = None,
    barrios: Optional[list[str]] = None,
    mercados: Optional[list[str]] = None,
) -> str:
    config = get_source_config(categoria)
    dimension_table = get_dimension_table(categoria)
    service_columns = get_dimension_service_columns(categoria)
    where_clause = build_filters_where(departamentos, localidades, barrios, mercados)
    combinacion_expr = _build_service_combination_expr(service_columns)

    aporte_ctes = []
    aporte_terms = []
    for index, (column, label) in enumerate(service_columns, start=1):
        alias = f"aporte_{index}"
        table_name = get_variable_table_name(column.lower(), categoria)
        aporte_ctes.append(
            f"""{alias} AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            SUM(COALESCE(ganancia_total, 0)) AS ganancia_{column.lower()}
        FROM {table_name}
        GROUP BY TipoIdentificacion, Identificacion
    )"""
        )
        aporte_terms.append(f"COALESCE({alias}.ganancia_{column.lower()}, 0)")

    aporte_ctes_sql = ",\n    ".join(aporte_ctes)
    aporte_join_sql = "\n".join(
        [
            f"""    LEFT JOIN aporte_{index} a{index}
        ON dim.TipoIdentificacion = a{index}.TipoIdentificacion
       AND dim.Identificacion = a{index}.Identificacion"""
            for index, _ in enumerate(service_columns, start=1)
        ]
    )
    aporte_expr = " + ".join(
        [f"COALESCE(a{index}.ganancia_{column.lower()}, 0)" for index, (column, _) in enumerate(service_columns, start=1)]
    )

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    ),
    {aporte_ctes_sql},
    clientes_aporte AS (
        SELECT
            dim.TipoIdentificacion,
            dim.Identificacion,
            CONCAT(dim.TipoIdentificacion, ' - ', dim.Identificacion) AS Cliente,
            {combinacion_expr} AS ServiciosActivos,
            {aporte_expr} AS AporteTotal
        FROM {dimension_table} dim
        INNER JOIN clientes_filtrados clientes
            ON dim.TipoIdentificacion = clientes.TipoIdentificacion
           AND dim.Identificacion = clientes.Identificacion
{aporte_join_sql}
    )
    SELECT
        TipoIdentificacion,
        Identificacion,
        Cliente,
        ServiciosActivos,
        AporteTotal
    FROM clientes_aporte
    WHERE ServiciosActivos <> ''
    ORDER BY AporteTotal DESC, Cliente
    LIMIT 5
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
    limit: Optional[int] = None,
):
    config = get_source_config(categoria)
    base_table = config["clientes"]
    dimension_table = DIMENSION_TABLES[categoria]

    where_clause = build_filters_where(
        departamentos=departamentos,
        localidades=localidades,
        barrios=barrios,
        mercados=mercados,
    )

    extra_service = config["servicio_extra_col"]
    limit_clause = build_limit_clause(limit)

    if categoria == "Residencial":
        extra = "dim.SAD, dim.Seguros"
    else: 
        extra = "dim.Efisoluciones"

    return f"""
    WITH 
        clientes_filtrados as (
        SELECT distinct tipoidentificacion, identificacion
        from {base_table}
        {where_clause})

    SELECT 
        dim.TipoIdentificacion,
        dim.Identificacion,
        dim.Consumo,
        dim.RTR,
        dim.Brilla,
        {extra},
        dim.Economica,
        dim.Cumplimiento,
        dim.Relacional,
        dim.Potencial
    FROM {dimension_table} dim
    INNER JOIN clientes_filtrados c
        on dim.tipoidentificacion=c.tipoidentificacion
        and dim.identificacion=c.identificacion
    {limit_clause}
    """

SERVICIOS_RESIDENCIAL = ["consumo", "rtr", "sad", "seguros", "brilla"]
SERVICIOS_COMERCIAL = ["consumo", "rtr", "efisoluciones", "brilla"]

TIPOS_DETALLE = ["dimensiones", "indicadores", "variables"]

SERVICE_CLASSIFICATION_TABLES = {
    "Residencial": {
        "brilla": "analiticaefg.clienteintegral.brilla_residencial_consolidado_dimensiones",
    },
    "Comercial": {
        "brilla": "analiticaefg.clienteintegral.brilla_comercial_consolidado_dimensiones",
    },
}


def get_detalle_servicio_query(
    servicio,
    categoria,
    tipo_detalle,
    departamentos=None,
    localidades=None,
    barrios=None,
    mercados=None,
    limit: Optional[int] = None,
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

    limit_clause = build_limit_clause(limit)

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
    {limit_clause}
    """


def get_service_classification_query(
    categoria: str,
    servicio: str,
    departamentos=None,
    localidades=None,
    barrios=None,
    mercados=None,
) -> str:
    service_table = SERVICE_CLASSIFICATION_TABLES.get(categoria, {}).get(servicio.lower())
    if not service_table:
        raise ValueError(f"No hay clasificación disponible para {servicio} en {categoria}.")

    config = get_source_config(categoria)
    where_clause = build_filters_where(
        departamentos=departamentos,
        localidades=localidades,
        barrios=barrios,
        mercados=mercados,
    )

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    )
    SELECT
        COALESCE(det.ClasificacionRFM, 'Sin clasificación') AS ClasificacionRFM,
        COUNT(*) AS clientes
    FROM {service_table} det
    INNER JOIN clientes_filtrados clientes
        ON det.TipoIdentificacion = clientes.TipoIdentificacion
       AND det.Identificacion = clientes.Identificacion
    GROUP BY COALESCE(det.ClasificacionRFM, 'Sin clasificación')
    ORDER BY clientes DESC, ClasificacionRFM
    """


def get_service_classification_profile_query(
    categoria: str,
    servicio: str,
    departamentos=None,
    localidades=None,
    barrios=None,
    mercados=None,
) -> str:
    service_table = SERVICE_CLASSIFICATION_TABLES.get(categoria, {}).get(servicio.lower())
    if not service_table:
        raise ValueError(f"No hay clasificación disponible para {servicio} en {categoria}.")

    config = get_source_config(categoria)
    where_clause = build_filters_where(
        departamentos=departamentos,
        localidades=localidades,
        barrios=barrios,
        mercados=mercados,
    )

    return f"""
    WITH clientes_filtrados AS (
        SELECT DISTINCT
            TipoIdentificacion,
            Identificacion
        FROM {config['clientes']}
        {where_clause}
    )
    SELECT
        AVG(COALESCE(det.Economica, 0)) AS Economica,
        AVG(COALESCE(det.Cumplimiento, 0)) AS Cumplimiento,
        AVG(COALESCE(det.Relacional, 0)) AS Relacional,
        AVG(COALESCE(det.Potencial, 0)) AS Potencial
    FROM {service_table} det
    INNER JOIN clientes_filtrados clientes
        ON det.TipoIdentificacion = clientes.TipoIdentificacion
       AND det.Identificacion = clientes.Identificacion
    """
