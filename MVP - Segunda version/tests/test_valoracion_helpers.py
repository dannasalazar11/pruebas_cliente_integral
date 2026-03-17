import unittest

import pandas as pd

from core.session import clear_state_mapping
from features.valoracion_integral.filters import get_dependent_options
from features.valoracion_integral.formatters import format_millions, format_number, human_format
from features.valoracion_integral.models import DashboardFilters


class ValoracionHelpersTestCase(unittest.TestCase):
    def test_formatters(self) -> None:
        self.assertEqual(format_number(1234.56, 1), "1.234,6")
        self.assertEqual(format_millions(1500000), "1.5M")
        self.assertEqual(human_format(1200), "1.2K")

    def test_dependent_options_follow_selected_filters(self) -> None:
        df_options = pd.DataFrame(
            [
                {"departamento": "Caldas", "localidad": "Manizales", "barrio": "Centro"},
                {"departamento": "Caldas", "localidad": "Chinchina", "barrio": "Centro"},
                {"departamento": "Quindio", "localidad": "Armenia", "barrio": "Norte"},
            ]
        )

        localidades, barrios = get_dependent_options(df_options, ("Caldas",), ("Manizales",))
        self.assertEqual(localidades, ["Chinchina", "Manizales"])
        self.assertEqual(barrios, ["Centro"])

    def test_dashboard_filters_roundtrip_payload(self) -> None:
        filters = DashboardFilters(categoria="Comercial", mercados=("CALDAS",), barrios=("Centro",))
        restored = DashboardFilters.from_payload(filters.to_payload())
        self.assertEqual(restored, filters)

    def test_clear_state_mapping_only_removes_page_scoped_keys(self) -> None:
        session_mapping = {
            "seccion_activa": "valoracion_integral",
            "dashboard_filters_applied": {},
            "info_selected_service": "RTR",
            "other_key": 123,
        }
        clear_state_mapping(session_mapping, preserve_keys={"seccion_activa"})
        self.assertIn("seccion_activa", session_mapping)
        self.assertIn("other_key", session_mapping)
        self.assertNotIn("dashboard_filters_applied", session_mapping)
        self.assertNotIn("info_selected_service", session_mapping)


if __name__ == "__main__":
    unittest.main()
