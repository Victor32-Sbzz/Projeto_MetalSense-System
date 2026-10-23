# MetalSense – Sistema Inteligente de Manutenção Preditiva & Monitoramento IoT

---

## 📌 Sobre o Projeto

**MetalSense** é um protótipo desenvolvido pela equipe **TechForge** (curso técnico em Desenvolvimento de Sistemas) que monitoriza máquinas industriais em tempo real. O sistema captura indicadores operacionais (temperatura, corrente, vibração, tempo de operação) via simulação IoT, persiste os dados em SQLite e utiliza um algoritmo simples de detecção de anomalias (desvio percentual) para gerar alertas.

A aplicação foi reestruturada para focar na **interface desktop em PyQt5** e em um **servidor TCP** que recebe as leituras dos sensores. Todos os componentes web/Streamlit, API REST, scripts de simulação avançada e arquivos de configuração Docker/Alembic foram removidos, pois não são utilizados pela lógica atual.

---

## 🏗️ Arquitetura Atual
```
[Sensor Simulator] → TCP Socket → [Server] → SQLite DB → [Anomaly Detector]
                                           │
                                           ▼
                                      PyQt5 UI (desktop)
```
- **Sensor Simulator** (`desktop/services/telemetry_service.py`) gera leituras a cada 5 s.
- **Server** (`desktop/controllers/app_controller.py`) recebe os dados e grava em `metalsense.db`.
- **Anomaly Detector** (`desktop/services/worker_service.py`) analisa a nova amostra e cria alertas.
- **UI Desktop** (`desktop/views/main_window.py` e abas) exibe gráficos em tempo real, histórico e mensagens de alerta.

---

## 📁 Estrutura de Diretórios
| Pasta / Arquivo | Responsabilidade |
|-----------------|-------------------|
| `desktop/` | Código da aplicação desktop (PyQt5). |
| `desktop/models/` | Modelo `Machine` que representa uma máquina industrial. |
| `desktop/services/` | Serviços de telemetria (simulador) e worker (detecção). |
| `desktop/controllers/` | Controle da aplicação e comunicação com o servidor. |
| `desktop/views/` | Componentes da interface (dashboards, abas, cards). |
| `database.py` | Wrapper de acesso ao SQLite (CRUD). |
| `dados.py` | Funções auxiliares de carregamento e manipulação de dados. |
| `requirements.txt` | Dependências Python. |
| `tests/` | Suite de testes automatizados. |

---

## 🚀 Como Executar
### 1. Instalar dependências
```bash
pip install -r requirements.txt
```
### 2. Rodar a aplicação desktop
```bash
python desktop/main.py
```
A janela do PyQt5 será aberta, iniciando o servidor interno, a captura simulada de sensores e a visualização dos dados.

### 3. Executar a suite de testes (opcional)
```bash
pytest
# ou
python -m unittest discover tests -v
```
---

## 👥 Equipe
- **Carmelita Azevedo** – Líder de Projeto
- **Ariane Pereira** – Designer UI (PyQt5)
- **Victor Miguel** – Desenvolvedor (backend, lógica de captura)
- **Miguel Freire** – Analista de Testes (QA)
- **Matheus Santos** – Analista de Testes (QA)

---

## 📄 Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
