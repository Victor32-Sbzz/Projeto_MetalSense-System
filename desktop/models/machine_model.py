"""
Modelos de dados e Entidades do Domínio MetalSense.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class TelemetriaLeitura:
    """Representa uma leitura pontual de sensores industriais."""
    timestamp: str
    temperatura: float
    vibracao: float
    consumo: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetriaLeitura":
        return cls(
            timestamp=data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            temperatura=float(data.get("temperatura", 0.0)),
            vibracao=float(data.get("vibracao", 0.0)),
            consumo=float(data.get("consumo", 0.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "temperatura": round(self.temperatura, 2),
            "vibracao": round(self.vibracao, 2),
            "consumo": round(self.consumo, 2),
        }


@dataclass
class Maquina:
    """Entidade que representa um equipamento monitorado pelo MetalSense."""
    id: int
    nome: str
    status: str = "sem dados"
    historico: List[TelemetriaLeitura] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Maquina":
        historico_raw = data.get("historico", [])
        leituras = [TelemetriaLeitura.from_dict(item) for item in historico_raw]
        return cls(
            id=int(data.get("id", 0)),
            nome=str(data.get("nome", "Sem Nome")).strip(),
            status=str(data.get("status", "sem dados")).strip().lower(),
            historico=leituras,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "status": self.status,
            "historico": [item.to_dict() for item in self.historico],
        }
