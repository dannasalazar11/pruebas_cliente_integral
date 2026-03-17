import unittest

from repositories.dashboard_queries import (
    build_filters_where,
    build_in_clause,
    get_clasificacion_integral_query,
    get_dimension_table,
    get_kpis_query,
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

    def test_get_source_config_uses_category_mapping(self) -> None:
        config = get_source_config("Residencial")
        self.assertEqual(config["servicio_extra_col"], "sad")

    def test_get_dimension_table_uses_category_mapping(self) -> None:
        self.assertIn("dimensiones_comercial", get_dimension_table("Comercial"))

    def test_get_kpis_query_uses_expected_table(self) -> None:
        query = get_kpis_query("Comercial")
        self.assertIn("modelo_datosclientecomercial", query)
        self.assertEqual(query.count("PorcentajeClientesMasDeUnServicio"), 1)

    def test_clasificacion_query_contains_single_dimension_cte(self) -> None:
        query = get_clasificacion_integral_query("Residencial")
        self.assertEqual(query.count("WITH base_filtrada"), 1)
        self.assertEqual(query.count("clasif AS"), 1)


if __name__ == "__main__":
    unittest.main()
