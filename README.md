# MetalSense: monitoramento e manutenção preditiva IoT

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-48%2F48%20passing-brightgreen.svg)]()
[![Team](https://img.shields.io/badge/team-TechForge-orange.svg)]()

Plataforma de telemetria e análise preditiva para equipamentos industriais. O sistema coleta dados de sensores, identifica desvios de operação e gera ordens de serviço antes que as máquinas parem.

Desenvolvido pelo grupo TechForge no curso Técnico em Desenvolvimento de Sistemas.

---

## Funcionalidades

- **Análise multivariada:** cruza dados de vibração, temperatura e corrente elétrica para isolar falhas mecânicas como desgaste de rolamento ou sobrecarga.
- **Health Score contínuo:** calcula uma nota de 0 a 100% para a saúde de cada máquina, considerando desvio padrão (2.5 sigma) e taxa de variação térmica (dT/dt).
- **Gateway IoT:** API REST com validação de limites físicos via Pydantic, limitação de taxa (rate limit) e autenticação por chave para microcontroladores como ESP32 e Raspberry Pi.
- **Persistência tolerante a falhas:** suporte a PostgreSQL com TimescaleDB, fallback local em SQLite com modo WAL e gravação atômica em disco para evitar perda de dados por queda de energia ou concorrência.
- **Simulador de falhas:** ferramenta de linha de comando para injetar cenários de desgaste mecânico, aquecimento e sobrecarga elétrica.
- **Relatórios:** exportação de histórico em CSV e emissão de laudos técnicos em HTML.
- **Duas interfaces de uso:** painel web em Streamlit e terminal CLI para uso local.

---

## Arquitetura

```text
[Sensores / ESP32 / Gateway de Campo]
                 │
                 ▼
       ┌──────────────────┐
       │   API REST IoT   │ <── Ingestão HTTP (POST /api/telemetria)
       └─────────┬────────┘
                 ▼
 ┌───────────────────────────────┐
 │ Persistência e Banco de Dados │ <── TimescaleDB / PostgreSQL / SQLite WAL
 └───────────────┬───────────────┘
                 ▼
       ┌───────────────────┐
       │ Motor de Análise  │ <── Health Score, tendências e diagnóstico
       └─────────┬─────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
 ┌──────────────┐  ┌──────────────┐
 │  Streamlit   │  │ Terminal CLI │
 │   (app.py)   │  │  (main.py)   │
 └──────────────┘  └──────────────┘
```

---

## Módulos do sistema

| Módulo | Função |
|---|---|
| `api.py` | Gateway REST com endpoints de ingestão, probes `/health` e `/ready`, autenticação e rate limit. |
| `analytics.py` | Cálculo do Health Score (0 a 100%), derivadas térmicas e detecção de anomalias por 2.5 sigma. |
| `maquinas.py` | Cadastro, atualização de estado operacional e validações de limites de processo. |
| `database.py` | Gerenciador de conexão SQLAlchemy com suporte a pool PostgreSQL/TimescaleDB e SQLite WAL. |
| `dados.py` | Camada de persistência local atômica com trava de leitura e escrita multithread. |
| `config.py` | Configuração centralizada do ambiente e validação de chaves conforme Twelve-Factor. |
| `schemas.py` | Modelos Pydantic v2 com validação física de dados dos sensores e prevenção de clock drift. |
| `security.py` | Autenticação por token/API key em tempo constante e controle de taxa com Flask-Limiter. |
| `logger.py` | Emissor de logs estruturados em formato JSON com identificador de requisição (request id). |
| `simulador_iot.py` | Gerador de telemetria com cenários pré-configurados de falha mecânica. |
| `relatorios.py` | Geração de laudos técnicos em HTML e exportação de dados em CSV. |
| `app.py` | Painel de controle web em Streamlit. |
| `main.py` | Interface de linha de comando para operação no terminal. |
| `tests/` | Suíte com 48 testes automatizados para regras de negócio, integrações e API. |

---

## Como executar

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Rodar os testes

```bash
python -m unittest discover tests -v
```

Ou com pytest:

```bash
pytest
```

### 3. Subir com Docker Compose (opcional)

Para rodar a API (Gunicorn), o painel Streamlit, o banco TimescaleDB e o Redis de forma integrada:

```bash
docker compose up --build -d
```

### 4. Execução manual dos serviços

**Painel Web (Streamlit):**
```bash
streamlit run app.py
```

**Interface de Terminal (CLI):**
```bash
python main.py
```

**API REST:**
```bash
python api.py
```
A API roda por padrão na porta 5000 (`http://localhost:5000`).

**Simulador de Sensores:**
```bash
python simulador_iot.py --id 1 --cenario rolamento --ciclos 5 --intervalo 1.0
```

---

## Equipe

Projeto desenvolvido pelo grupo TechForge no curso Técnico em Desenvolvimento de Sistemas.
