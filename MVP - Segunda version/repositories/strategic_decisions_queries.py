from collections.abc import Sequence

from repositories.dashboard_queries import get_dimension_service_columns


CONTRACT_TABLES = {
    "Residencial": "analiticaefg.clienteintegral.modelo_contratosresidencial",
    "Comercial": "analiticaefg.clienteintegral.modelo_contratoscomercial",
}


def escape_sql_value(value: str) -> str:
    return value.replace("'", "''")


def get_service_options(categoria: str) -> list[str]:
    return [label for _, label in get_dimension_service_columns(categoria)]


def _get_service_key_lookup(categoria: str) -> dict[str, str]:
    return {label: column.lower() for column, label in get_dimension_service_columns(categoria)}


def get_contract_table(categoria: str) -> str:
    if categoria not in CONTRACT_TABLES:
        raise ValueError(f"Categoría no válida: {categoria}")
    return CONTRACT_TABLES[categoria]


def get_consolidado_dimension_table(servicio: str, categoria: str) -> str:
    categoria_sql = categoria.lower()
    return f"analiticaefg.clienteintegral.{servicio}_{categoria_sql}_consolidado_dimensiones"


def get_consolidado_variable_table(servicio: str, categoria: str) -> str:
    categoria_sql = categoria.lower()
    return f"analiticaefg.clienteintegral.{servicio}_{categoria_sql}_consolidado_variables"


def get_table_columns_query(full_name: str) -> str:
    catalog, schema, table = full_name.split(".")
    return f"""
    SELECT column_name
    FROM system.information_schema.columns
    WHERE table_catalog = '{escape_sql_value(catalog)}'
      AND table_schema = '{escape_sql_value(schema)}'
      AND table_name = '{escape_sql_value(table)}'
    ORDER BY ordinal_position
    """


def get_consolidar_query(
    categoria: str,
    servicios: Sequence[str],
    top_n: int,
    variable_columns_by_service: dict[str, Sequence[str]] | None = None,
) -> str:
    if not servicios:
        raise ValueError("Debe seleccionar al menos un servicio.")
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor que cero.")

    variable_columns_by_service = variable_columns_by_service or {}
    service_lookup = _get_service_key_lookup(categoria)
    normalized_services: list[tuple[str, str]] = []
    for servicio in servicios:
        service_key = service_lookup.get(servicio)
        if not service_key:
            raise ValueError(f"Servicio no válido para {categoria}: {servicio}")
        normalized_services.append((servicio, service_key))

    dim_tables = {
        servicio_label: get_consolidado_dimension_table(service_key, categoria)
        for servicio_label, service_key in normalized_services
    }
    variable_tables = {
        servicio_label: get_consolidado_variable_table(service_key, categoria)
        for servicio_label, service_key in normalized_services
    }

    selects_scores: list[str] = []
    joins_dim: list[str] = []
    from_clause = ""
    for index, (servicio_label, _) in enumerate(normalized_services):
        alias = f"d{index}"
        if index == 0:
            from_clause = f"{dim_tables[servicio_label]} {alias}"
        else:
            joins_dim.append(
                f"""INNER JOIN {dim_tables[servicio_label]} {alias}
                    ON d0.TipoIdentificacion = {alias}.TipoIdentificacion
                   AND d0.Identificacion = {alias}.Identificacion"""
            )

        selects_scores.append(
            f"""(
                0.55 * (0.55 * {alias}.Relacional + 0.45 * {alias}.Cumplimiento)
                + 0.30 * {alias}.Economica
                + 0.15 * (1 - {alias}.Potencial)
            ) AS score_{service_lookup[servicio_label]}"""
        )

    score_columns = [f"score_{service_key}" for _, service_key in normalized_services]
    score_final_expr = score_columns[0] if len(score_columns) == 1 else f"least({', '.join(score_columns)})"

    joins_vars: list[str] = []
    selects_vars: list[str] = []
    for servicio_label, service_key in normalized_services:
        alias = f"v_{service_key}"
        joins_vars.append(
            f"""LEFT JOIN {variable_tables[servicio_label]} {alias}
                ON b.TipoIdentificacion = {alias}.TipoIdentificacion
               AND b.Identificacion = {alias}.Identificacion"""
        )
        for column in variable_columns_by_service.get(servicio_label, []):
            selects_vars.append(f"{alias}.`{column}` AS `{service_key}_{column}`")

    select_vars_sql = ""
    if selects_vars:
        select_vars_sql = ",\n    " + ",\n    ".join(selects_vars)

    contract_table = get_contract_table(categoria)

    return f"""
    WITH base AS (
        SELECT
            d0.TipoIdentificacion,
            d0.Identificacion,
            {", ".join(selects_scores)}
        FROM {from_clause}
        {" ".join(joins_dim)}
    ),
    scored AS (
        SELECT *,
            {score_final_expr} AS Score_CON
        FROM base
    )
    SELECT
        b.TipoIdentificacion,
        b.Identificacion,
        b.Score_CON,
        c.Contratos,
        c.ContratosActivos{select_vars_sql}
    FROM scored b
    LEFT JOIN {contract_table} c
        ON b.TipoIdentificacion = c.TipoIdentificacion
       AND b.Identificacion = c.Identificacion
    {" ".join(joins_vars)}
    ORDER BY b.Score_CON DESC
    LIMIT {top_n}
    """


def get_recuperar_query(
    categoria: str,
    servicio: str,
    top_n: int,
    variable_columns: Sequence[str] | None = None,
) -> str:
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor que cero.")

    service_lookup = _get_service_key_lookup(categoria)
    service_key = service_lookup.get(servicio)
    if not service_key:
        raise ValueError(f"Servicio no válido para {categoria}: {servicio}")

    dim_table = get_consolidado_dimension_table(service_key, categoria)
    variable_table = get_consolidado_variable_table(service_key, categoria)
    variable_columns = variable_columns or ()

    select_vars_sql = ""
    if variable_columns:
        select_vars_sql = ",\n    " + ",\n    ".join(
            [f"v.`{column}` AS `{service_key}_{column}`" for column in variable_columns]
        )

    contract_table = get_contract_table(categoria)

    return f"""
    WITH base AS (
        SELECT
            d.TipoIdentificacion,
            d.Identificacion,
            (0.55 * (1 - d.Cumplimiento) + 0.45 * (1 - d.Relacional)) AS Deterioro,
            d.Economica AS Valor,
            (0.65 * d.Potencial + 0.35 * d.Relacional) AS Viabilidad
        FROM {dim_table} d
    ),
    scored AS (
        SELECT *,
            (0.55 * Deterioro + 0.30 * Valor + 0.15 * Viabilidad) AS Score_REC
        FROM base
    )
    SELECT
        s.TipoIdentificacion,
        s.Identificacion,
        s.Score_REC,
        c.Contratos,
        c.ContratosActivos{select_vars_sql}
    FROM scored s
    LEFT JOIN {contract_table} c
        ON s.TipoIdentificacion = c.TipoIdentificacion
       AND s.Identificacion = c.Identificacion
    LEFT JOIN {variable_table} v
        ON s.TipoIdentificacion = v.TipoIdentificacion
       AND s.Identificacion = v.Identificacion
    ORDER BY s.Score_REC DESC
    LIMIT {top_n}
    """


def get_fidelizar_query(
    categoria: str,
    servicio_ancla: str,
    servicio_objetivo: str,
    top_n: int,
    variable_columns_ancla: Sequence[str] | None = None,
    variable_columns_objetivo: Sequence[str] | None = None,
) -> str:
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor que cero.")

    service_lookup = _get_service_key_lookup(categoria)
    ancla_key = service_lookup.get(servicio_ancla)
    objetivo_key = service_lookup.get(servicio_objetivo)
    if not ancla_key:
        raise ValueError(f"Servicio ancla no válido para {categoria}: {servicio_ancla}")
    if not objetivo_key:
        raise ValueError(f"Servicio objetivo no válido para {categoria}: {servicio_objetivo}")
    if ancla_key == objetivo_key:
        raise ValueError("El servicio ancla y el servicio objetivo deben ser diferentes.")

    dim_table_ancla = get_consolidado_dimension_table(ancla_key, categoria)
    dim_table_objetivo = get_consolidado_dimension_table(objetivo_key, categoria)
    var_table_ancla = get_consolidado_variable_table(ancla_key, categoria)
    var_table_objetivo = get_consolidado_variable_table(objetivo_key, categoria)
    variable_columns_ancla = variable_columns_ancla or ()
    variable_columns_objetivo = variable_columns_objetivo or ()

    extra_columns: list[str] = []
    for column in variable_columns_ancla:
        extra_columns.append(f"va.`{column}` AS `{ancla_key}_{column}`")
    for column in variable_columns_objetivo:
        extra_columns.append(f"vo.`{column}` AS `{objetivo_key}_{column}`")
    extra_sql = ""
    if extra_columns:
        extra_sql = ",\n    " + ",\n    ".join(extra_columns)

    contract_table = get_contract_table(categoria)

    return f"""
    WITH base AS (
        SELECT
            a.TipoIdentificacion,
            a.Identificacion,
            a.Economica AS econ_ancla,
            a.Cumplimiento AS cump_ancla,
            a.Relacional AS rel_ancla,
            o.Economica AS econ_obj,
            o.Relacional AS rel_obj,
            o.Potencial AS pot_obj
        FROM {dim_table_ancla} a
        INNER JOIN {dim_table_objetivo} o
            ON a.TipoIdentificacion = o.TipoIdentificacion
           AND a.Identificacion = o.Identificacion
    ),
    scores AS (
        SELECT *,
            (0.4 * cump_ancla + 0.35 * rel_ancla + 0.25 * econ_ancla) AS F_ancla,
            (0.5 * pot_obj + 0.3 * (1 - rel_obj) + 0.2 * (1 - econ_obj)) AS B_objetivo,
            (0.6 * cump_ancla + 0.4 * rel_ancla) AS S_cliente
        FROM base
    ),
    final_scores AS (
        SELECT
            TipoIdentificacion,
            Identificacion,
            (0.5 * B_objetivo + 0.3 * F_ancla + 0.2 * S_cliente) AS Score_FID
        FROM scores
    )
    SELECT
        s.TipoIdentificacion,
        s.Identificacion,
        s.Score_FID,
        c.Contratos,
        c.ContratosActivos{extra_sql}
    FROM final_scores s
    LEFT JOIN {contract_table} c
        ON s.TipoIdentificacion = c.TipoIdentificacion
       AND s.Identificacion = c.Identificacion
    LEFT JOIN {var_table_ancla} va
        ON s.TipoIdentificacion = va.TipoIdentificacion
       AND s.Identificacion = va.Identificacion
    LEFT JOIN {var_table_objetivo} vo
        ON s.TipoIdentificacion = vo.TipoIdentificacion
       AND s.Identificacion = vo.Identificacion
    ORDER BY s.Score_FID DESC
    LIMIT {top_n}
    """


def get_potenciar_query(
    categoria: str,
    servicios: Sequence[str],
    top_n: int,
    variable_columns_by_service: dict[str, Sequence[str]] | None = None,
) -> str:
    if not servicios:
        raise ValueError("Debe seleccionar al menos un servicio.")
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor que cero.")

    variable_columns_by_service = variable_columns_by_service or {}
    service_lookup = _get_service_key_lookup(categoria)
    normalized_services: list[tuple[str, str]] = []
    for servicio in servicios:
        service_key = service_lookup.get(servicio)
        if not service_key:
            raise ValueError(f"Servicio no válido para {categoria}: {servicio}")
        normalized_services.append((servicio, service_key))

    dim_tables = {
        servicio_label: get_consolidado_dimension_table(service_key, categoria)
        for servicio_label, service_key in normalized_services
    }
    variable_tables = {
        servicio_label: get_consolidado_variable_table(service_key, categoria)
        for servicio_label, service_key in normalized_services
    }

    selects_scores: list[str] = []
    joins_dim: list[str] = []
    from_clause = ""
    for index, (servicio_label, service_key) in enumerate(normalized_services):
        alias = f"t{index}"
        if index == 0:
            from_clause = f"{dim_tables[servicio_label]} {alias}"
        else:
            joins_dim.append(
                f"""INNER JOIN {dim_tables[servicio_label]} {alias}
                    ON t0.TipoIdentificacion = {alias}.TipoIdentificacion
                   AND t0.Identificacion = {alias}.Identificacion"""
            )
        selects_scores.append(
            f"""(
                0.45 * {alias}.Potencial
                + 0.30 * {alias}.Economica
                + 0.15 * {alias}.Relacional
                + 0.10 * {alias}.Cumplimiento
            ) AS score_{service_key}"""
        )

    score_avg_formula = " + ".join([f"score_{service_key}" for _, service_key in normalized_services])

    joins_vars: list[str] = []
    selects_vars: list[str] = []
    for servicio_label, service_key in normalized_services:
        alias = f"v_{service_key}"
        joins_vars.append(
            f"""LEFT JOIN {variable_tables[servicio_label]} {alias}
                ON b.TipoIdentificacion = {alias}.TipoIdentificacion
               AND b.Identificacion = {alias}.Identificacion"""
        )
        for column in variable_columns_by_service.get(servicio_label, []):
            selects_vars.append(f"{alias}.`{column}` AS `{service_key}_{column}`")

    select_vars_sql = ""
    if selects_vars:
        select_vars_sql = ",\n    " + ",\n    ".join(selects_vars)

    contract_table = get_contract_table(categoria)

    return f"""
    WITH base AS (
        SELECT
            t0.TipoIdentificacion,
            t0.Identificacion,
            {", ".join(selects_scores)}
        FROM {from_clause}
        {" ".join(joins_dim)}
    ),
    scored AS (
        SELECT *,
            ({score_avg_formula}) / {len(normalized_services)} AS Score_POT
        FROM base
    )
    SELECT
        b.TipoIdentificacion,
        b.Identificacion,
        b.Score_POT,
        c.Contratos,
        c.ContratosActivos{select_vars_sql}
    FROM scored b
    LEFT JOIN {contract_table} c
        ON b.TipoIdentificacion = c.TipoIdentificacion
       AND b.Identificacion = c.Identificacion
    {" ".join(joins_vars)}
    ORDER BY b.Score_POT DESC
    LIMIT {top_n}
    """
