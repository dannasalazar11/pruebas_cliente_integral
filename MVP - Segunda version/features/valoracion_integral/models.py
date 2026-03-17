from dataclasses import dataclass


@dataclass(frozen=True)
class DashboardFilters:
    periodo: str = "Marzo 2026"
    categoria: str = "Residencial"
    mercados: tuple[str, ...] = ()
    departamentos: tuple[str, ...] = ()
    localidades: tuple[str, ...] = ()
    barrios: tuple[str, ...] = ()

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "DashboardFilters":
        payload = payload or {}
        return cls(
            periodo=str(payload.get("periodo", cls.periodo)),
            categoria=str(payload.get("categoria", cls.categoria)),
            mercados=tuple(payload.get("mercados", cls.mercados)),
            departamentos=tuple(payload.get("departamentos", cls.departamentos)),
            localidades=tuple(payload.get("localidades", cls.localidades)),
            barrios=tuple(payload.get("barrios", cls.barrios)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "periodo": self.periodo,
            "categoria": self.categoria,
            "mercados": list(self.mercados),
            "departamentos": list(self.departamentos),
            "localidades": list(self.localidades),
            "barrios": list(self.barrios),
        }
