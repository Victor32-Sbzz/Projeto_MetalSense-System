"""
Serviço de Domínio para Telemetria e Monitoramento Preditivo Industrial.
Isola completamente as regras de negócio de qualquer elemento visual (SoC).
"""
import json
import csv
import os
import random
import statistics
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

from desktop.config import DATA_FILE, LIMITES_OPERACIONAIS
from desktop.models.machine_model import Maquina, TelemetriaLeitura


class TelemetryService:
    """Gerencia a persistência, telemetria e análise preditiva do MetalSense."""

    def __init__(self, data_path: Path = DATA_FILE):
        self.data_path = Path(data_path)

    def carregar_dados_brutos(self) -> Dict[str, Any]:
        """Lê o arquivo JSON de dados de forma segura com fallback."""
        if not self.data_path.exists():
            dados_iniciais = {"maquinas": []}
            self.salvar_dados_brutos(dados_iniciais)
            return dados_iniciais

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"maquinas": []}

    def salvar_dados_brutos(self, dados: Dict[str, Any]) -> None:
        """Salva os dados atomicamente para evitar corrupção durante I/O."""
        temp_file = self.data_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, self.data_path)

    def listar_maquinas(self) -> List[Maquina]:
        """Retorna todas as máquinas cadastradas como objetos tipados."""
        dados = self.carregar_dados_brutos()
        maquinas_raw = dados.get("maquinas", [])
        return [Maquina.from_dict(m) for m in maquinas_raw]

    def obter_maquina_por_id(self, id_maquina: int) -> Optional[Maquina]:
        """Localiza uma máquina pelo ID."""
        for m in self.listar_maquinas():
            if m.id == id_maquina:
                return m
        return None

    def cadastrar_maquina(self, nome: str) -> Maquina:
        """Cadastra uma nova máquina com ID incremental e validação de nome."""
        nome_limpo = (nome or "").strip()
        if not nome_limpo:
            raise ValueError("O nome da máquina não pode ser vazio ou conter apenas espaços.")

        dados = self.carregar_dados_brutos()
        maquinas = dados.get("maquinas", [])
        ids = [m.get("id") for m in maquinas if isinstance(m.get("id"), int)]
        novo_id = (max(ids) + 1) if ids else 1

        nova_maquina = Maquina(id=novo_id, nome=nome_limpo, status="sem dados", historico=[])
        maquinas.append(nova_maquina.to_dict())
        dados["maquinas"] = maquinas
        self.salvar_dados_brutos(dados)
        return nova_maquina

    def remover_maquina(self, id_maquina: int) -> bool:
        """Remove a máquina especificada pelo ID."""
        dados = self.carregar_dados_brutos()
        maquinas = dados.get("maquinas", [])
        maquinas_filtradas = [m for m in maquinas if m.get("id") != id_maquina]

        if len(maquinas_filtradas) < len(maquinas):
            dados["maquinas"] = maquinas_filtradas
            self.salvar_dados_brutos(dados)
            return True
        return False

    def gerar_leitura_simulada(self, gerar_anomalia: bool = False) -> TelemetriaLeitura:
        """Simula leitura com faixas normais ou picos críticos para teste de anomalia."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not gerar_anomalia:
            # Faixa operacional segura
            temperatura = round(random.uniform(55.0, 68.0), 2)
            vibracao = round(random.uniform(2.0, 4.5), 2)
            consumo = round(random.uniform(250.0, 380.0), 2)
        else:
            # Injeção controlada de falha crítica
            tipo = random.choice(["temperatura", "vibracao", "consumo", "combinada"])
            if tipo == "temperatura":
                temperatura = round(random.uniform(88.0, 115.0), 2)
                vibracao = round(random.uniform(2.0, 4.5), 2)
                consumo = round(random.uniform(250.0, 380.0), 2)
            elif tipo == "vibracao":
                temperatura = round(random.uniform(55.0, 68.0), 2)
                vibracao = round(random.uniform(9.0, 16.5), 2)
                consumo = round(random.uniform(250.0, 380.0), 2)
            elif tipo == "consumo":
                temperatura = round(random.uniform(55.0, 68.0), 2)
                vibracao = round(random.uniform(2.0, 4.5), 2)
                consumo = round(random.uniform(550.0, 850.0), 2)
            else:
                temperatura = round(random.uniform(86.0, 110.0), 2)
                vibracao = round(random.uniform(8.5, 15.0), 2)
                consumo = round(random.uniform(520.0, 800.0), 2)

        return TelemetriaLeitura(
            timestamp=timestamp,
            temperatura=temperatura,
            vibracao=vibracao,
            consumo=consumo,
        )

    def analisar_maquina(self, id_maquina: int) -> Tuple[str, str]:
        """
        Executa motor preditivo de inferência.
        Retorna (novo_status, mensagem_diagnostico).
        """
        dados = self.carregar_dados_brutos()
        for m in dados.get("maquinas", []):
            if m.get("id") == id_maquina:
                historico = m.get("historico", [])
                if len(historico) < 2:
                    m["status"] = "sem dados"
                    self.salvar_dados_brutos(dados)
                    return "sem dados", "Histórico insuficiente para análise preditiva (mínimo de 2 medições necessárias)."

                ultima = historico[-1]
                motivos = []

                # 1. Checagem de limites operacionais absolutos
                if ultima["temperatura"] > LIMITES_OPERACIONAIS["temperatura_max"]:
                    motivos.append(f"Temperatura crítica ({ultima['temperatura']} °C > {LIMITES_OPERACIONAIS['temperatura_max']} °C)")
                if ultima["vibracao"] > LIMITES_OPERACIONAIS["vibracao_max"]:
                    motivos.append(f"Vibração excessiva ({ultima['vibracao']} mm/s > {LIMITES_OPERACIONAIS['vibracao_max']} mm/s)")
                if ultima["consumo"] > LIMITES_OPERACIONAIS["consumo_max"]:
                    motivos.append(f"Sobrecarga elétrica ({ultima['consumo']} W > {LIMITES_OPERACIONAIS['consumo_max']} W)")

                # 2. Avaliação de desvio padrão estatístico em relação ao histórico próprio
                if not motivos and len(historico) >= 3:
                    baseline = historico[:-1]
                    for chave, nome, unidade in [
                        ("temperatura", "Temperatura", "°C"),
                        ("vibracao", "Vibração", "mm/s"),
                        ("consumo", "Consumo", "W"),
                    ]:
                        valores = [h[chave] for h in baseline]
                        media = statistics.mean(valores)
                        desvio = statistics.stdev(valores) if len(valores) > 1 else 0.0

                        if desvio > 0.05:
                            dist = abs(ultima[chave] - media)
                            if dist > (LIMITES_OPERACIONAIS["desvio_padrao_fator"] * desvio):
                                motivos.append(
                                    f"{nome} fora do desvio histórico ({ultima[chave]} {unidade} vs média {media:.2f} {unidade})"
                                )

                if motivos:
                    m["status"] = "anomalia"
                    self.salvar_dados_brutos(dados)
                    return "anomalia", f"Anomalia detectada: {', '.join(motivos)}!"
                else:
                    m["status"] = "normal"
                    self.salvar_dados_brutos(dados)
                    return "normal", "Equipamento operando dentro dos padrões nominais seguros."

        return "sem dados", "Máquina não encontrada no registro."

    def registrar_leitura(
        self, id_maquina: int, leitura: Optional[TelemetriaLeitura] = None, gerar_anomalia: bool = False
    ) -> Tuple[Optional[TelemetriaLeitura], str, str]:
        """
        Adiciona uma leitura ao histórico da máquina e aciona diagnóstico automático.
        Retorna (leitura_adicionada, novo_status, diagnostico_texto).
        """
        dados = self.carregar_dados_brutos()
        for m in dados.get("maquinas", []):
            if m.get("id") == id_maquina:
                if leitura is None:
                    leitura = self.gerar_leitura_simulada(gerar_anomalia=gerar_anomalia)

                m.setdefault("historico", []).append(leitura.to_dict())
                self.salvar_dados_brutos(dados)

                status, diag = self.analisar_maquina(id_maquina)
                return leitura, status, diag

        return None, "sem dados", "Máquina não localizada."

    def exportar_relatorio_csv(self, id_maquina: int, output_file: Path) -> bool:
        """Exporta histórico de telemetria da máquina para formato CSV."""
        maquina = self.obter_maquina_por_id(id_maquina)
        if not maquina or not maquina.historico:
            return False

        with open(output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Timestamp", "Temperatura_C", "Vibracao_mms", "Consumo_W"])
            for h in maquina.historico:
                writer.writerow([h.timestamp, h.temperatura, h.vibracao, h.consumo])
        return True
