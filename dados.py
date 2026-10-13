"""
Módulo de Persistência Híbrida do MetalSense.
Combina escrita atômica em disco com lock thread-safe e sincronização
com a camada relacional/séries temporais SQLite em modo WAL.
"""

import json
import os
import shutil
import threading
from typing import Dict, Any
from logger import logger

ARQUIVO_DADOS = "dados.json"

# Lock reentrante para sincronização de I/O em múltiplos threads
_FILE_LOCK = threading.RLock()


def carregar_dados(caminho_arquivo: str = ARQUIVO_DADOS) -> Dict[str, Any]:
    """
    Carrega os dados das máquinas a partir do arquivo JSON com controle de concorrência.
    Se o arquivo não existir ou estiver corrompido, recupera com segurança gerando backup.
    """
    with _FILE_LOCK:
        if not os.path.exists(caminho_arquivo):
            dados = {"maquinas": []}
            salvar_dados(dados, caminho_arquivo)
            return dados

        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Arquivo {caminho_arquivo} corrompido ou inválido ({e}). Iniciando recuperação.")
            backup_path = f"{caminho_arquivo}.corrompido.bak"
            try:
                shutil.copy(caminho_arquivo, backup_path)
                logger.info(f"Backup de segurança gerado em: {backup_path}")
            except Exception as ex:
                logger.error(f"Falha ao gerar backup: {ex}")

            dados = {"maquinas": []}
            salvar_dados(dados, caminho_arquivo)
            return dados


def salvar_dados(dados: Dict[str, Any], caminho_arquivo: str = ARQUIVO_DADOS) -> None:
    """
    Salva os dados de forma atômica e thread-safe no arquivo JSON especificado.
    Sincroniza automaticamente com a base de dados relacional se for o arquivo padrão.
    """
    with _FILE_LOCK:
        arquivo_temp = f"{caminho_arquivo}.tmp"
        with open(arquivo_temp, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)

        # Substituição atômica no sistema de arquivos
        os.replace(arquivo_temp, caminho_arquivo)

        # Sincronização secundária com SQLite para queries analíticas avançadas
        if caminho_arquivo == ARQUIVO_DADOS:
            try:
                _sincronizar_com_banco(dados)
            except Exception as e:
                logger.debug(f"Sincronização secundária com banco SQLite adiada: {e}")


def _sincronizar_com_banco(dados: Dict[str, Any]) -> None:
    """Sincroniza em background o estado das máquinas com a base relacional."""
    try:
        from database import db, transacao_escrita, agora_utc
        from sqlalchemy import text
        agora = agora_utc()
        with transacao_escrita(db.engine) as conn:
            for m in dados.get("maquinas", []):
                conn.execute(
                    text("""
                        INSERT INTO maquinas (id, nome, status, criado_em, atualizado_em)
                        VALUES (:id, :nome, :status, :criado_em, :atualizado_em)
                        ON CONFLICT(id) DO UPDATE SET
                            nome = excluded.nome,
                            status = excluded.status,
                            atualizado_em = :atualizado_em
                    """),
                    {
                        "id": m["id"],
                        "nome": m["nome"],
                        "status": m.get("status", "sem dados"),
                        "criado_em": agora,
                        "atualizado_em": agora,
                    }
                )
    except Exception as e:
        logger.debug(f"Sincronização secundária com banco de dados adiada: {e}")
