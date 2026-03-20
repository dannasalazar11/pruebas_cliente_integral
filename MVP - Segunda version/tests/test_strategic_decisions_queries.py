import unittest

from repositories.strategic_decisions_queries import (
    get_consolidar_query,
    get_contract_table,
    get_fidelizar_query,
    get_potenciar_query,
    get_recuperar_query,
    get_table_columns_query,
)


class StrategicDecisionsQueriesTestCase(unittest.TestCase):
    def test_get_contract_table_uses_current_tables(self) -> None:
        self.assertIn("modelo_contratosresidencial", get_contract_table("Residencial"))
        self.assertIn("modelo_contratoscomercial", get_contract_table("Comercial"))

    def test_get_table_columns_query_uses_information_schema(self) -> None:
        query = get_table_columns_query(
            "analiticaefg.clienteintegral.consumo_residencial_consolidado_variables"
        )
        self.assertIn("system.information_schema.columns", query)
        self.assertIn("table_catalog = 'analiticaefg'", query)
        self.assertIn("table_schema = 'clienteintegral'", query)
        self.assertIn("table_name = 'consumo_residencial_consolidado_variables'", query)

    def test_get_consolidar_query_uses_composite_keys_instead_of_idcliente(self) -> None:
        query = get_consolidar_query(
            categoria="Residencial",
            servicios=["Consumo", "Brilla"],
            top_n=50,
            variable_columns_by_service={
                "Consumo": ["ganancia_total"],
                "Brilla": ["edad_cliente"],
            },
        )
        self.assertNotIn("IdCliente", query)
        self.assertIn("d0.TipoIdentificacion = d1.TipoIdentificacion", query)
        self.assertIn("d0.Identificacion = d1.Identificacion", query)
        self.assertIn("b.TipoIdentificacion = c.TipoIdentificacion", query)
        self.assertIn("b.Identificacion = c.Identificacion", query)
        self.assertIn("consumo_residencial_consolidado_dimensiones", query)
        self.assertIn("brilla_residencial_consolidado_dimensiones", query)
        self.assertIn("consumo_residencial_consolidado_variables", query)
        self.assertIn("brilla_residencial_consolidado_variables", query)
        self.assertIn("score_consumo", query)
        self.assertIn("score_brilla", query)
        self.assertIn("least(score_consumo, score_brilla)", query)
        self.assertIn("LIMIT 50", query)

    def test_get_recuperar_query_uses_composite_keys_and_service_tables(self) -> None:
        query = get_recuperar_query(
            categoria="Comercial",
            servicio="Brilla",
            top_n=25,
            variable_columns=["ganancia_total", "antiguedad"],
        )
        self.assertNotIn("IdCliente", query)
        self.assertIn("brilla_comercial_consolidado_dimensiones", query)
        self.assertIn("brilla_comercial_consolidado_variables", query)
        self.assertIn("s.TipoIdentificacion = c.TipoIdentificacion", query)
        self.assertIn("s.Identificacion = c.Identificacion", query)
        self.assertIn("s.TipoIdentificacion = v.TipoIdentificacion", query)
        self.assertIn("s.Identificacion = v.Identificacion", query)
        self.assertIn("AS Score_REC", query)
        self.assertIn("LIMIT 25", query)

    def test_get_fidelizar_query_uses_composite_keys_and_two_service_tables(self) -> None:
        query = get_fidelizar_query(
            categoria="Residencial",
            servicio_ancla="Consumo",
            servicio_objetivo="Brilla",
            top_n=40,
            variable_columns_ancla=["ganancia_total"],
            variable_columns_objetivo=["edad_cliente"],
        )
        self.assertNotIn("IdCliente", query)
        self.assertIn("consumo_residencial_consolidado_dimensiones", query)
        self.assertIn("brilla_residencial_consolidado_dimensiones", query)
        self.assertIn("consumo_residencial_consolidado_variables", query)
        self.assertIn("brilla_residencial_consolidado_variables", query)
        self.assertIn("a.TipoIdentificacion = o.TipoIdentificacion", query)
        self.assertIn("a.Identificacion = o.Identificacion", query)
        self.assertIn("s.TipoIdentificacion = c.TipoIdentificacion", query)
        self.assertIn("s.Identificacion = c.Identificacion", query)
        self.assertIn("AS Score_FID", query)
        self.assertIn("LIMIT 40", query)

    def test_get_potenciar_query_uses_composite_keys_and_average_score(self) -> None:
        query = get_potenciar_query(
            categoria="Comercial",
            servicios=["Consumo", "Brilla"],
            top_n=30,
            variable_columns_by_service={
                "Consumo": ["ganancia_total"],
                "Brilla": ["edad_cliente"],
            },
        )
        self.assertNotIn("IdCliente", query)
        self.assertIn("consumo_comercial_consolidado_dimensiones", query)
        self.assertIn("brilla_comercial_consolidado_dimensiones", query)
        self.assertIn("consumo_comercial_consolidado_variables", query)
        self.assertIn("brilla_comercial_consolidado_variables", query)
        self.assertIn("t0.TipoIdentificacion = t1.TipoIdentificacion", query)
        self.assertIn("t0.Identificacion = t1.Identificacion", query)
        self.assertIn("AS Score_POT", query)
        self.assertIn("(score_consumo + score_brilla) / 2", query)
        self.assertIn("LIMIT 30", query)


if __name__ == "__main__":
    unittest.main()
