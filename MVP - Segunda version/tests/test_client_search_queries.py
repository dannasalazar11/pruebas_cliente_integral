import unittest

from repositories.client_search_queries import (
    get_cliente_contratos_raw_query,
    get_cliente_detalle_servicio_query,
    get_cliente_dimensiones_query,
    get_cliente_raw_query,
    get_contratos_detalle_query,
    get_tipo_identificacion_options_query,
)


class ClientSearchQueriesTestCase(unittest.TestCase):
    def test_tipo_identificacion_options_query_uses_contracts_table(self) -> None:
        query = get_tipo_identificacion_options_query()
        self.assertIn("modelo_datosclienteresidencial", query)
        self.assertIn("SELECT DISTINCT TipoIdentificacion", query)

    def test_cliente_raw_query_deduplicates_person_records(self) -> None:
        query = get_cliente_raw_query("CC", "123")
        self.assertIn("modelo_dimcliente", query)
        self.assertIn("QUALIFY ROW_NUMBER()", query)
        self.assertIn("TipoIdentificacion = 'CC'", query)
        self.assertIn("Identificacion = '123'", query)

    def test_cliente_contratos_raw_query_filters_person(self) -> None:
        query = get_cliente_contratos_raw_query("CC", "123")
        self.assertIn("modelo_datosclienteresidencial", query)
        self.assertIn("TipoIdentificacion = 'CC'", query)
        self.assertIn("Identificacion = '123'", query)

    def test_contratos_detalle_query_filters_by_category_and_contracts(self) -> None:
        query = get_contratos_detalle_query(["1001", "1002"], "Comercial")
        self.assertIn("dwhbiefg.comun.dimcontrato", query)
        self.assertIn("LEFT JOIN analiticaefg.clienteintegral.modelo_dimubicacion", query)
        self.assertIn("c.Valido = 1", query)
        self.assertIn("c.Categoria = 2", query)
        self.assertIn("c.Contrato IN ('1001', '1002')", query)

    def test_cliente_dimensiones_query_uses_dimension_table_by_universe(self) -> None:
        query = get_cliente_dimensiones_query("CC", "123", "Residencial")
        self.assertIn("dimensiones_residencial", query)
        self.assertIn("TipoIdentificacion = 'CC'", query)
        self.assertIn("Identificacion = '123'", query)

    def test_cliente_detalle_servicio_query_targets_service_table(self) -> None:
        query = get_cliente_detalle_servicio_query("CC", "123", "Comercial", "brilla", "indicadores")
        self.assertIn("brilla_comercial_consolidado_indicadores", query)
        self.assertIn("TipoIdentificacion = 'CC'", query)
        self.assertIn("Identificacion = '123'", query)


if __name__ == "__main__":
    unittest.main()
