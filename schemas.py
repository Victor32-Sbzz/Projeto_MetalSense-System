"""
Módulo de Validação Estrita de Schemas e Sanitarização de Telemetria Industrial.
Utiliza Pydantic v2 para assegurar integridade física, tipagem rígida e
sanitização de dados antes do processamento preditivo ou persistência.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# Limites operacionais de engenharia industrial
TEMP_MIN, TEMP_MAX = -40.0, 300.0
VIB_MIN, VIB_MAX = 0.0, 100.0
POT_MIN, POT_MAX = 0.0, 50000.0


class TelemetriaPayload(BaseModel):
    """Payload de uma medição pontual de sensor industrial."""

    id_maquina: int = Field(..., gt=0, description="Identificador único da máquina (inteiro positivo)")
    temperatura: float = Field(
        ...,
        ge=TEMP_MIN,
        le=TEMP_MAX,
        description=f"Temperatura em graus Celsius ({TEMP_MIN} a {TEMP_MAX}°C)"
    )
    vibracao: float = Field(
        ...,
        ge=VIB_MIN,
        le=VIB_MAX,
        description=f"Vibração mecânica em mm/s ({VIB_MIN} a {VIB_MAX} mm/s)"
    )
    consumo: float = Field(
        ...,
        ge=POT_MIN,
        le=POT_MAX,
        description=f"Potência / Consumo elétrico em Watts ({POT_MIN} a {POT_MAX} W)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data/hora da medição (ISO 8601 ou YYYY-MM-DD HH:MM:SS)"
    )

    @field_validator("temperatura", "vibracao", "consumo")
    @classmethod
    def arredondar_metricas(cls, v: float) -> float:
        return round(float(v), 2)

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalizar_timestamp(cls, v: any) -> Optional[datetime]:
        if v is None or v == "":
            return datetime.now(timezone.utc)
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        if isinstance(v, str):
            v_str = v.strip()
            # Suporta formato legado 'YYYY-MM-DD HH:MM:SS'
            try:
                dt = datetime.strptime(v_str, "%Y-%m-%d %H:%M:%S")
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
            # Suporta formato ISO 8601
            try:
                dt = datetime.fromisoformat(v_str.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except ValueError:
                raise ValueError("Formato de timestamp inválido. Utilize 'YYYY-MM-DD HH:MM:SS' ou padrão ISO 8601.")
        raise ValueError("Timestamp deve ser uma string ou datetime.")

    @model_validator(mode="after")
    def validar_relogio(self) -> TelemetriaPayload:
        if self.timestamp:
            agora = datetime.now(timezone.utc)
            limite_futuro = agora + timedelta(minutes=5)
            if self.timestamp > limite_futuro:
                raise ValueError("Timestamp rejeitado: data/hora está adiantada no futuro em mais de 5 minutos.")
        return self


class TelemetriaLotePayload(BaseModel):
    """Payload para envio em lote (buffer offline de gateways de campo)."""

    leituras: List[TelemetriaPayload] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Lista de leituras agregadas (máximo 500 por requisição)"
    )


class MaquinaCadastroPayload(BaseModel):
    """Payload para cadastro de novos ativos no parque fabril."""

    nome: str = Field(..., min_length=1, max_length=100, description="Nome ou identificador da máquina")

    @field_validator("nome")
    @classmethod
    def validar_nome_nao_vazio(cls, v: str) -> str:
        limpo = v.strip()
        if not limpo:
            raise ValueError("O nome da máquina não pode conter apenas espaços em branco.")
        return limpo
