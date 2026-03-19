from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CustomerSearchRequest:
    universo: str = "Residencial"
    tipo_identificacion: str = ""
    identificacion: str = ""
    searched: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "CustomerSearchRequest":
        payload = payload or {}
        return cls(
            universo=str(payload.get("universo", cls.universo)),
            tipo_identificacion=str(payload.get("tipo_identificacion", cls.tipo_identificacion)),
            identificacion=str(payload.get("identificacion", cls.identificacion)),
            searched=bool(payload.get("searched", cls.searched)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "universo": self.universo,
            "tipo_identificacion": self.tipo_identificacion,
            "identificacion": self.identificacion,
            "searched": self.searched,
        }


@dataclass(frozen=True)
class CustomerProfile:
    nombre: str
    apellido: str
    tipo_identificacion: str
    identificacion: str


@dataclass(frozen=True)
class CustomerSearchResult:
    profile: CustomerProfile | None
    contratos: pd.DataFrame
    dimensiones: pd.DataFrame
    servicios_activos: tuple[str, ...]
    detalle_servicios: dict[str, dict[str, pd.DataFrame]]
