import unittest

from repositories.dashboard_queries import (
    build_filters_where,
    build_in_clause,
    build_limit_clause,
    get_clientes_mayor_aporte_query,
    get_clasificacion_integral_query,
    get_combinaciones_servicios_query,
    get_consolidado_general_query,
    get_detalle_servicio_query,
    get_dimension_table,
    get_kpis_query,
    get_numero_servicios_query,
    get_penetracion_servicios_query,
    get_service_classification_query,
    get_service_classification_profile_query,
    get_source_config,
    map_ui_markets_to_db_values,
)


class DashboardQueriesTestCase(unittest.TestCase):
    def test_map_ui_markets_to_db_values(self) -> None:
        self.assertEqual(
            map_ui_markets_to_db_values(["CALDAS", "OTRO"]),
            ["MERCADO RELEVANTE -ASE CALDAS", "OTRO"],
        )

    def test_build_in_clause_escapes_single_quotes(self) -> None:
        clause = build_in_clause("departamento", ["O'Higgins"])
        self.assertIn("O''Higgins", clause)
        self.assertIn("departamento IN", clause)

    def test_build_filters_where_includes_all_selected_filters(self) -> None:
        where_clause = build_filters_where(
            departamentos=["Antioquia"],
            localidades=["Medellin"],
            barrios=["Centro"],
            mercados=["CALDAS"],
        )
        self.assertIn("departamento IN ('Antioquia')", where_clause)
        self.assertIn("localidad IN ('Medellin')", where_clause)
        self.assertIn("barrio IN ('Centro')", where_clause)
        self.assertIn("MercadoRelevante IN ('MERCADO RELEVANTE -ASE CALDAS')", where_clause)

    def test_build_limit_clause_validates_positive_limit(self) -> None:
        self.assertEqual(build_limit_clause(100).strip(), "LIMIT 100")
        with self.assertRaises(ValueError):
            build_limit_clause(0)

    def test_get_source_config_uses_category_mapping(self) -> None:
        config = get_source_config("Residencial")
        self.assertEqual(config["servicio_extra_col"], "sad")

    def test_get_dimension_table_uses_category_mapping(self) -> None:
        self.assertIn("dimensiones_comercial", get_dimension_table("Comercial"))

    def test_get_kpis_query_uses_expected_table(self) -> None:
        query = get_kpis_query("Comercial")
        self.assertIn("modelo_datosclientecomercial", query)
        self.assertIn("dimensiones_comercial", query)
        self.assertIn("COALESCE(dim.efisoluciones, 0)", query)
        self.assertIn("COALESCE(dim.brilla, 0)", query)
        self.assertEqual(query.count("PorcentajeClientesTresOMasServicios"), 1)
        self.assertIn("NumeroServicios >= 3", query)

    def test_clasificacion_query_contains_single_dimension_cte(self) -> None:
        query = get_clasificacion_integral_query("Residencial")
        self.assertEqual(query.count("WITH base_filtrada"), 1)
        self.assertEqual(query.count("clasif AS"), 1)

    def test_consolidado_general_query_can_limit_preview_rows(self) -> None:
        query = get_consolidado_general_query("Residencial", limit=100)
        self.assertIn("LIMIT 100", query)

    def test_detalle_servicio_query_can_limit_preview_rows(self) -> None:
        query = get_detalle_servicio_query(
            servicio="consumo",
            categoria="Residencial",
            tipo_detalle="dimensiones",
            limit=100,
        )
        self.assertIn("LIMIT 100", query)

    def test_detalle_servicio_query_supports_new_service_tables(self) -> None:
        residencial_query = get_detalle_servicio_query(
            servicio="seguros",
            categoria="Residencial",
            tipo_detalle="variables",
        )
        self.assertIn("seguros_residencial_consolidado_variables", residencial_query)

        comercial_query = get_detalle_servicio_query(
            servicio="brilla",
            categoria="Comercial",
            tipo_detalle="indicadores",
        )
        self.assertIn("brilla_comercial_consolidado_indicadores", comercial_query)

    def test_numero_servicios_query_uses_residential_dimensions_table(self) -> None:
        query = get_numero_servicios_query("Residencial")
        self.assertIn("dimensiones_residencial", query)
        self.assertIn("COALESCE(dim.consumo, 0)", query)
        self.assertIn("COALESCE(dim.rtr, 0)", query)
        self.assertIn("COALESCE(dim.sad, 0)", query)
        self.assertIn("COALESCE(dim.Brilla, 0)", query)
        self.assertIn("COALESCE(dim.seguros, 0)", query)
        self.assertIn("HAVING NumeroServicios BETWEEN 1 AND 5", query)

    def test_numero_servicios_query_uses_commercial_dimensions_table(self) -> None:
        query = get_numero_servicios_query("Comercial")
        self.assertIn("dimensiones_comercial", query)
        self.assertIn("COALESCE(dim.efisoluciones, 0)", query)
        self.assertIn("COALESCE(dim.brilla, 0)", query)
        self.assertIn("HAVING NumeroServicios BETWEEN 1 AND 4", query)

    def test_penetracion_query_uses_dimension_services_by_category(self) -> None:
        residencial_query = get_penetracion_servicios_query("Residencial")
        self.assertIn("SUM(Brilla)", residencial_query)
        self.assertIn("SUM(seguros)", residencial_query)

        comercial_query = get_penetracion_servicios_query("Comercial")
        self.assertIn("SUM(efisoluciones)", comercial_query)
        self.assertIn("SUM(brilla)", comercial_query)

    def test_combinaciones_query_uses_dimension_table_and_labels(self) -> None:
        query = get_combinaciones_servicios_query("Residencial")
        self.assertIn("dimensiones_residencial", query)
        self.assertIn("CONCAT_WS(' + '", query)
        self.assertIn("'Consumo'", query)
        self.assertIn("'Seguros'", query)
        self.assertIn("LIMIT 5", query)

    def test_aporte_query_uses_variable_tables_and_services(self) -> None:
        query = get_clientes_mayor_aporte_query("Comercial")
        self.assertIn("consumo_comercial_consolidado_variables", query)
        self.assertIn("rtr_comercial_consolidado_variables", query)
        self.assertIn("efisoluciones_comercial_consolidado_variables", query)
        self.assertIn("brilla_comercial_consolidado_variables", query)
        self.assertIn("SUM(COALESCE(ganancia_total, 0))", query)
        self.assertIn("ServiciosActivos", query)
        self.assertIn("LIMIT 5", query)

    def test_service_classification_query_uses_brilla_dimension_table(self) -> None:
        query = get_service_classification_query("Residencial", "brilla")
        self.assertIn("brilla_residencial_consolidado_dimensiones", query)
        self.assertIn("ClasificacionRFM", query)
        self.assertIn("modelo_datosclienteresidencial", query)

    def test_service_classification_profile_query_averages_dimension_columns(self) -> None:
        query = get_service_classification_profile_query("Comercial", "brilla")
        self.assertIn("AVG(COALESCE(det.Economica, 0))", query)
        self.assertIn("AVG(COALESCE(det.Cumplimiento, 0))", query)
        self.assertIn("AVG(COALESCE(det.Relacional, 0))", query)
        self.assertIn("AVG(COALESCE(det.Potencial, 0))", query)
        self.assertIn("brilla_comercial_consolidado_dimensiones", query)


if __name__ == "__main__":
    unittest.main()
