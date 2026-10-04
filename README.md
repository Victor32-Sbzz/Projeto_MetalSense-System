# MetalSense — Sistema Inteligente de Manutenção Preditiva & Monitoramento IoT

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-38%2F38%20passing-brightgreen.svg)]()
[![Team](https://img.shields.io/badge/team-TechForge-orange.svg)]()

> Sistema de detecção antecipada de anomalias industriais, análise preditiva multivariada e ingestão de telemetria IoT para prevenção de paradas não planejadas (Indústria 4.0).

---

## 📌 Sobre o Projeto

O **MetalSense** foi concebido pelo grupo **TechForge** no curso Técnico em Desenvolvimento de Sistemas. O sistema transforma dados brutos de sensores de campo (temperatura, vibração mecânica e consumo elétrico) em **informações de saúde do ativo em tempo real** e **ordens de serviço preditivas**, evitando quebras catastróficas e paradas inesperadas na linha de produção.

---

## ⚡ Diferenciais Tecnológicos

1. **Análise Multivariada Real:** Não se limita a limites fixos; avalia correlações físicas (ex: Vibração Alta + Temperatura Alta = Desgaste de Rolamento).
2. **Health Score (0 a 100%):** Índice contínuo de integridade do ativo por máquina, avaliando volatilidade e velocidade de degradação térmica ($dT/dt$).
3. **Gateway IoT com API REST:** Rota HTTP de alta performance (`/api/telemetria`) pronta para receber dados de microcontroladores (ESP32, Arduino, Raspberry Pi).
4. **Simulador de Falhas Físicas:** Injeção programática de desbalanceamento mecânico, falha de arrefecimento e sobrecarga elétrica.
5. **Auditoria e Laudos Automatizados:** Exportação instantânea de histórico em CSV e emissão de laudos técnicos em HTML e Ordens de Serviço (OS).
6. **Múltiplas Interfaces:** Dashboard Web reativo em Streamlit e Console CLI com cores ANSI.

---

## 🏗️ Arquitetura do Sistema

```text
[Sensores Industriais / ESP32 / Gateway]
                 │
                 ▼
       ┌──────────────────┐
       │   API REST IoT   │ <── Ingestão via HTTP (POST /api/telemetria)
       └─────────┬────────┘
                 ▼
   ┌──────────────────────────┐
   │  Persistência Resiliente │ <── Escrita atômica & backup contra corrupção
   │       (dados.py)         │
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │    Motor de Analytics    │ <── Health Score, Tendências (dT/dt)
   │      (analytics.py)      │     e Diagnóstico de Causa-Raiz
   └─────────────┬────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
┌──────────────┐   ┌──────────────┐
│  Streamlit   │   │ Terminal CLI │
│   (app.py)   │   │  (main.py)   │
└──────────────┘   └──────────────┘
```

---

## 📁 Estrutura de Módulos

| Módulo | Responsabilidade |
|---|---|
| `analytics.py` | Motor preditivo: Health Score (0-100%), tendências temporais e hipóteses de falha mecânica. |
| `maquinas.py` | Lógica de negócio de máquinas, validações e detecção de anomalias por $2.5\sigma$ e limites críticos. |
| `dados.py` | Camada de persistência segura, gravação atômica (`.tmp`) e recuperação contra corrupção. |
| `simulador_iot.py`| Simulador de sensores físicos industriais com cenários de rolamento, aquecimento e sobrecarga. |
| `relatorios.py` | Emissão de laudos de auditoria técnica (HTML), ordens de serviço (OS) e exportação CSV. |
| `api.py` | API REST Flask para ingestão de telemetria externa e integração com sistemas SCADA/MES. |
| `app.py` | Dashboard interativo Web (Streamlit) com KPIs, gráficos em tempo real e controles de simulação. |
| `main.py` | Interface de terminal profissional com menu interativo, cores ANSI e diagnóstico instantâneo. |
| `tests/` | Suíte de testes automatizados com 38 testes unitários (100% de cobertura de regras de negócio). |

---

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar a Suíte de Testes Automatizados (38 Testes)
```bash
python -m unittest discover tests -v
# ou
pytest
```

### 3. Iniciar o Dashboard Web (Streamlit)
```bash
streamlit run app.py
```

### 4. Iniciar a Interface em Terminal (CLI)
```bash
python main.py
```

### 5. Iniciar a API REST do Gateway IoT
```bash
python api.py
```
*Disponível em: `http://127.0.0.1:5000` (Endpoint de telemetria: `POST /api/telemetria`)*

### 6. Executar o Simulador de Sensores IoT
```bash
python simulador_iot.py --id 1 --cenario rolamento --ciclos 5 --intervalo 1.0
```

---

## 👥 Equipe & Desenvolvimento

Projeto desenvolvido pelo grupo **TechForge** no curso Técnico em Desenvolvimento de Sistemas.
