from dataclasses import dataclass


@dataclass(frozen=True)
class ConsolidarRequest:
    categoria: str = "Residencial"
    servicios: tuple[str, ...] = ()
    top_n: int = 100
    searched: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "ConsolidarRequest":
        payload = payload or {}
        servicios_raw = payload.get("servicios", ())
        if isinstance(servicios_raw, str):
            servicios = (servicios_raw,)
        else:
            servicios = tuple(str(value) for value in servicios_raw or ())

        return cls(
            categoria=str(payload.get("categoria", cls.categoria)),
            servicios=servicios,
            top_n=int(payload.get("top_n", cls.top_n)),
            searched=bool(payload.get("searched", cls.searched)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "categoria": self.categoria,
            "servicios": list(self.servicios),
            "top_n": self.top_n,
            "searched": self.searched,
        }


@dataclass(frozen=True)
class RecuperarRequest:
    categoria: str = "Residencial"
    servicio: str = ""
    top_n: int = 100
    searched: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "RecuperarRequest":
        payload = payload or {}
        return cls(
            categoria=str(payload.get("categoria", cls.categoria)),
            servicio=str(payload.get("servicio", cls.servicio)),
            top_n=int(payload.get("top_n", cls.top_n)),
            searched=bool(payload.get("searched", cls.searched)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "categoria": self.categoria,
            "servicio": self.servicio,
            "top_n": self.top_n,
            "searched": self.searched,
        }


@dataclass(frozen=True)
class FidelizarRequest:
    categoria: str = "Residencial"
    servicio_ancla: str = ""
    servicio_objetivo: str = ""
    top_n: int = 100
    searched: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "FidelizarRequest":
        payload = payload or {}
        return cls(
            categoria=str(payload.get("categoria", cls.categoria)),
            servicio_ancla=str(payload.get("servicio_ancla", cls.servicio_ancla)),
            servicio_objetivo=str(payload.get("servicio_objetivo", cls.servicio_objetivo)),
            top_n=int(payload.get("top_n", cls.top_n)),
            searched=bool(payload.get("searched", cls.searched)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "categoria": self.categoria,
            "servicio_ancla": self.servicio_ancla,
            "servicio_objetivo": self.servicio_objetivo,
            "top_n": self.top_n,
            "searched": self.searched,
        }


@dataclass(frozen=True)
class PotenciarRequest:
    categoria: str = "Residencial"
    servicios: tuple[str, ...] = ()
    top_n: int = 100
    searched: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, object] | None) -> "PotenciarRequest":
        payload = payload or {}
        servicios_raw = payload.get("servicios", ())
        if isinstance(servicios_raw, str):
            servicios = (servicios_raw,)
        else:
            servicios = tuple(str(value) for value in servicios_raw or ())

        return cls(
            categoria=str(payload.get("categoria", cls.categoria)),
            servicios=servicios,
            top_n=int(payload.get("top_n", cls.top_n)),
            searched=bool(payload.get("searched", cls.searched)),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "categoria": self.categoria,
            "servicios": list(self.servicios),
            "top_n": self.top_n,
            "searched": self.searched,
        }
