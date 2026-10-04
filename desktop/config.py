"""
Módulo de Configuração e Constantes do MetalSense Desktop.
Define paletas de cores para o tema escuro industrial, limites operacionais e caminhos.
"""
from pathlib import Path

# Caminho base e arquivos de dados
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "dados.json"

# Limites Operacionais de Segurança (Faixas Críticas)
LIMITES_OPERACIONAIS = {
    "temperatura_max": 85.0,     # °C
    "vibracao_max": 8.0,         # mm/s
    "consumo_max": 500.0,        # W
    "desvio_padrao_fator": 2.5,  # Desvio estatístico padrão
}

# Paleta Visual - Tema Escuro Industrial (Modern Dark TechForge)
THEME_COLORS = {
    "bg_dark": "#0f172a",          # Fundo escuro principal
    "bg_card": "#1e293b",          # Fundo de containers/cards
    "bg_card_alt": "#334155",      # Fundo secundário para hover/destaques
    "text_primary": "#f8fafc",     # Texto principal claro
    "text_secondary": "#94a3b8",   # Texto secundário/subtítulo
    "accent_blue": "#3b82f6",      # Azul TechForge
    "accent_cyan": "#06b6d4",      # Ciano para telemetria
    "status_normal": "#22c55e",    # Verde de conformidade
    "status_anomaly": "#ef4444",   # Vermelho de anomalia/alerta
    "status_unknown": "#64748b",   # Cinza sem dados
    "border": "#475569",           # Borda suave
}
