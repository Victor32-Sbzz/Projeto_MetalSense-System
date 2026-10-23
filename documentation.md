# MetalSense – Documentação Completa

## MÓDULO 1 – CONCEPÇÃO DE NEGÓCIO
### 1.1 Identificação do Projeto

- **Nome da equipe:** TechForge
- **Nome da solução:** MetalSense
- **Instituição de ensino:** Escola Rodolfo de Oliveira
- **Curso / Projeto:** SESI/SENAI – Dr. Celso Charuri
- **Curso técnico:** Desenvolvimento de Sistemas
- **Turma:** 2º B
- **Professores orientadores:** Guilherme e Luciana
- **Empresa de referência:** Metalforte Indústria Metalúrgica
- **Setor industrial de referência:** Corte e Dobra de Metais
- **Integrantes:**
  - Carmelita Azevedo (Líder)
  - Ariane Pereira (Designer UI)
  - Victor Miguel (Desenvolvedor)
  - Miguel Freire (QA)
  - Matheus Santos (QA)

### 1.2 Apresentação da Solução

MetalSense é um sistema de monitoramento inteligente que coleta, armazena e analisa indicadores operacionais de máquinas industriais, permitindo a detecção precoce de anomalias.

- **Tecnologias principais:** IoT (simulação de sensores), Python 3.13, SQLite, PyQt5, Pandas, Scikit‑Learn.
- **Objetivo:** transformar o histórico de operação em referência de “comportamento normal” e identificar desvios que possam indicar falhas.

### 1.3 Identificação do Problema

Máquinas industriais que operam fora dos parâmetros esperados podem gerar falhas ou paradas não programadas. O monitoramento tradicional baseado em limites fixos costuma perder variações sutis que antecedem esses eventos.

### 1.4 Motivação

- **Industrial:** garantir a continuidade da produção reduzindo tempos de parada.
- **Acadêmica/Técnica:** aplicar conceitos de IoT, bancos de dados, análise de dados e Machine Learning em um protótipo real.

### 1.5 Objetivo Geral

Desenvolver um sistema de monitoramento inteligente capaz de coletar e armazenar indicadores de funcionamento de máquinas industriais, estabelecer referências de comportamento normal e identificar alterações que possam indicar possíveis falhas, usando análise de dados histórica.

### 1.6 Objetivos Específicos

- Prototipar um modelo de máquina industrial (simulador de sensores).
- Implementar comunicação IoT (socket/TCP) para transmissão de dados.
- Capturar indicadores relevantes (temperatura, corrente, vibração, tempo de operação).
- Desenvolver aplicação Python para receber, processar e persistir as informações.
- Armazenar o histórico em banco de dados (SQLite).
- Analisar os indicadores e detectar desvios em relação ao padrão histórico.
- Aplicar técnicas de ML (detecção de anomalias).
- Implementar interface gráfica (PyQt5) para visualização e alertas.
- Gerar relatórios/exportação CSV para auditoria.

### 1.7 Ramo Comercial Atendido

Setor industrial – monitoramento de máquinas em linhas de produção de corte e dobra de metais. O produto pode ser adaptado a outros equipamentos que requerem manutenção preditiva.

### 1.8 Diferencial da Solução

- **Histórico‑baseado:** a referência de “normal” é construída a partir dos próprios dados, não de limites estáticos.
- **Integração total:** captura → persistência → análise → visualização em um único fluxo.
- **Baixo custo:** uso de ferramentas open‑source e hardware enxuto (simulação).

### 1.9 Divisão de Responsabilidades

| Integrante | Papel | Responsabilidades |
|------------|-------|-------------------|
| Victor Miguel | Desenvolvedor (Dev) | Codificação back‑end, lógica de captura, camada de ML. |
| Ariane Pereira | Designer UI | Criação da UI em PyQt5, layout, experiência de usuário. |
| Matheus Santos | Analista de Testes (QA) | Elaboração e execução de casos de teste, verificação de requisitos não‑funcionais. |
| Miguel Freire | Analista de Testes (QA) | Apoio nos testes, validação de relatórios e documentação visual. |
| Carmelita Azevedo | Líder de Projeto | Coordenação, definição de cronograma, compilação da documentação e preparação da apresentação. |

### 1.10 Situação Atual do Projeto

- Código‑fonte implementado (captura, servidor, UI).
- Testes de integração concluídos.
- Interface gráfica está funcional (tabelas, gráficos, alertas).
- Documentação preliminar já escrita (este documento complementa).
- Próximas ações: revisão final, geração de artefatos (PDF/Word) e preparação da defesa.

### 1.11 Business Model Canvas

| Canvas Item | Descrição |
|-------------|-----------|
| **Escopo** | Sistema de monitoramento de equipamentos industriais (IoT + análise de dados). |
| **Segmento de clientes** | Indústrias de metalurgia, usinas de corte/dobra, fábricas de processos contínuos. |
| **Proposta de valor** | Redução de paradas não planejadas – manutenção preditiva baseada em histórico real; solução de baixo custo e rapidamente implantável. |
| **Canais** | Licença de software (instalação on‑premise), demos presenciais, documentação on‑line (GitHub). |
| **Relacionamento com cliente** | Suporte técnico remoto, treinamento de operadores, atualização de versão sem custos adicionais. |
| **Fluxo de receita** | Venda de licença anual + serviços de customização (integração a PLCs). |
| **Recursos principais** | Código‑fonte (Python), base de dados SQLite, modelo de detecção de anomalias, UI PyQt5. |
| **Atividades chave** | Desenvolvimento de firmware/sensores, coleta de dados, treinamento de modelo, suporte ao cliente. |
| **Parcerias** | Metalforte Indústria (caso de uso), fornecedores de sensores IoT, universidades para pesquisa de ML. |
| **Estrutura de custos** | Desenvolvimento (horas‑homem), infra‑estrutura (servidor local), manutenção de código, treinamento. |
| **Tempo de implementação** | MVP em 3 meses (captura + UI). Versão completa em 6 meses (ML avançado, integração PLC). |
| **Possíveis parcerias** | Empresas de automação (Siemens, Schneider) para integração com sistemas SCADA. |

---

## MÓDULO 2 – REGRAS
### 2.1 Requisitos Financeiros (funcionais)
| ID | Requisito | Onde está implementado |
|----|-----------|------------------------|
| RF‑01 | Captura de dados de sensores a cada 5 s e envio ao servidor. | src/sensor_simulator.py – função `generate_data()` |
| RF‑02 | Persistência de cada leitura no banco SQLite. | src/database.py – método `insert_measurement()` |
| RF‑03 | Exibição do histórico de medições com filtros de data. | ui/main_window.py – classe `HistoryTable` |
| RF‑04 | Detecção de anomalia comparando a leitura atual com a média dos últimos 30 min. | src/anomaly_detector.py – função `detect_anomaly()` |
| RF‑05 | Geração de alerta visual na UI quando anomalia for identificada. | ui/main_window.py – método `show_alert()` |
| RF‑06 | Exportação de relatório histórico em CSV. | src/export.py – função `export_csv()` |
| RF‑07 | Configuração dinâmica do intervalo de captura via interface. | ui/settings_dialog.py – classe `SettingsDialog` |

### 2.2 Requisitos Não‑Funcionais
| Categoria | Critério | Valor / Observação |
|-----------|----------|--------------------|
| **Desempenho** | Latência da captura ≤ 100 ms; atualização UI ≤ 200 ms. | Testado em PC i5‑8250U, Windows 10. |
| **Linguagem** | Python 3.13 (padrão do ambiente). | Utiliza bibliotecas padrão + pyqt5, pandas, scikit‑learn. |
| **Tempo de processamento** | Algoritmo de detecção < 50 ms por amostra. | Implementado com cálculo vetorial (NumPy). |
| **Uso de memória** | Processo ≤ 150 MB (incluindo UI). | Medido com `psutil`. |
| **Armazenamento** | DB SQLite ≤ 200 MB para 6 meses (≈ 10 k reg/dia). | Arquivo `metalsense.db`. |
| **IDE** | Visual Studio Code (extensões Python, Pylance). | |
| **Confiabilidade** | Disponibilidade ≥ 99 % em testes de 2 h. | |
| **Integridade** | Transações ACID no SQLite; backup diário automático (scripts/backup_db.sh). | |
| **Segurança** | Comunicação interna via sockets locais (sem exposição externa). | |
| **Portabilidade** | Compatível com Windows 10/11 e Linux (testado). | |
| **Restrições** | Nenhum requisito de hardware específico além de um PC com Python instalado. | |
| **Escalabilidade** | Arquitetura modular permite substituição do simulador por hardware real (MQTT, Modbus). | |

---

## MÓDULO 3 – MODELAÇÃO TÉCNICA
### 3.1 Fluxograma de Processos (texto descritivo)
```
Início
│
├─► Sensor Simulator gera dados (Temperatura, Corrente, Vibração, Tempo de operação) a cada 5 s
│
├─► Dados enviados por TCP socket ao Server (src/server.py)
│
├─► Server recebe → valida → persiste no SQLite (Database.insert_measurement)
│
├─► AnomalyDetector analisa a nova amostra:
│        ├─► Se desvio > threshold → cria registro em alerts e envia mensagem ao UI
│        └─► Caso contrário → prossegue
│
├─► UI (PyQt5) consulta BD:
│        ├─► Atualiza gráficos de tendência (temperatura, corrente, vibração)
│        ├─► Atualiza tabela de histórico (filtrável por data)
│        └─► Exibe alerta (campo vermelho) quando necessário
│
├─► Usuário pode:
│        ├─► Ajustar intervalo de captura (Settings)
│        ├─► Exportar CSV do histórico
│        └─► Encerrar aplicação
│
└─► Fim
```

---

## MÓDULO 4 – INFRAESTRUTURA
### 4.1 Bibliotecas Utilizadas e Funções/Classes Principais
| Biblioteca | Versão | Funções/Classes utilizadas | Propósito |
|------------|--------|----------------------------|----------|
| Python stdlib | 3.13 | `socket`, `threading`, `datetime`, `logging` | Comunicação, concorrência, registro de eventos. |
| pyqt5 | 5.15.9 | `QMainWindow`, `QTableWidget`, `QChartView`, `QMessageBox` | Interface gráfica. |
| sqlite3 | (builtin) | `connect`, `cursor`, `execute`, `commit` | Persistência dos dados de sensores e alertas. |
| pandas | 2.2.1 | `DataFrame`, `read_sql`, `to_csv` | Manipulação e exportação de tabelas. |
| scikit‑learn | 1.5.0 | `StandardScaler` (pre‑processamento futuro) | Base para possíveis algoritmos de ML avançados. |
| requests | 2.34.2 | `get` (download de imagens de diagramas) | Auxílio na geração de artefatos. |
| beautifulsoup4 | 4.15.0 | `BeautifulSoup` (parsing de HTML) | Conversão de documentação. |
| python‑docx | 1.2.0 | `Document`, `add_heading`, `add_paragraph`, `add_table`, `add_picture` | Criação de arquivos Word (script de apoio). |
| lxml | 6.1.3 | Parser XML/HTML rápido usado por BeautifulSoup. | Suporte ao parsing. |

**Principais classes do projeto**
- `SensorSimulator` (src/sensor_simulator.py): simula sensores, gera leituras aleatórias realistas.
- `Server` (src/server.py): aceita conexões, recebe mensagens, delega ao `Database`.
- `Database` (src/database.py): wrapper SQLite com métodos `insert_measurement`, `query_measurements`, `insert_alert`.
- `AnomalyDetector` (src/anomaly_detector.py): algoritmo simples de desvio percentual; retorna booleano + descrição.
- `MainWindow` (ui/main_window.py): janela principal – gráficos, tabela de histórico, painel de alertas.
- `SettingsDialog` (ui/settings_dialog.py): permite mudar intervalo de captura e parâmetros de alerta.
- `Exporter` (src/export.py): função `export_csv` que gera arquivo `historico_YYYYMMDD.csv`.
- `BackupScript` (scripts/backup_db.sh): script que copia `metalsense.db` para backup diário.

### 4.2 Mapeamento de Telas (descrição textual)
- **Dashboard (Main Window)** – gráficos de temperatura, corrente e vibração; tabela *History* (Data/Hora, Temp., Corr., Vib., Anomalia); painel de alertas em vermelho.
- **Configurações** – campo “Intervalo de captura” (spin‑box em segundos), campo “Threshold de anomalia” (percentual) e botão **Salvar**.
- **Exportação** – botão **Exportar CSV** que abre diálogo para escolher diretório de destino e gera `historico_YYYYMMDD.csv`.
- **Sobre** – texto estático com versão, equipe, licença e link para o repositório.

### 4.3 Banco de Dados
- **Tipo:** SQLite (`metalsense.db`).
- **Tabelas principais:**
  - `measurements` (id, timestamp, temperature, current, vibration, runtime)
  - `alerts` (id, measurement_id, alert_type, created_at)
- **Justificativa:** SQLite é leve, não requer servidor, oferece ACID e facilidade de distribuição – ideal para protótipos.
- **Melhorias futuras:** migração para PostgreSQL ou MySQL; persistência na nuvem via S3 ou RDS; backup automático integrado; camada ORM com SQLAlchemy.

---

## MÓDULO 5 – VERSIONAMENTO E ESTRUTURA
### 5.1 Repositório no GitHub
- **URL:** https://github.com/Victor32-Sbzz/Projeto_MetalSense-System
- **Licença:** MIT (arquivo `LICENSE`).
- **Estrutura de diretórios:**
```
Projeto_MetalSense-System/
│
├─ src/                     # Código‑fonte Python
│   ├─ sensor_simulator.py
│   ├─ server.py
│   ├─ database.py
│   ├─ anomaly_detector.py
│   ├─ export.py
│   └─ __init__.py
│
├─ ui/                      # Interface gráfica (PyQt5)
│   ├─ main_window.py
│   ├─ settings_dialog.py
│   └─ resources/           # ícones, imagens
│
├─ tests/                   # Testes (pytest)
│   ├─ test_database.py
│   ├─ test_anomaly.py
│   └─ ...
│
├─ docs/                    # Documentação extra
│   ├─ diagrams/            # PNGs dos fluxogramas e diagramas
│   └─ README.md            # Visão geral (ver seção abaixo)
│
├─ scripts/                 # Scripts auxiliares (backup, deploy)
│   └─ backup_db.sh
│
├─ requirements.txt         # Lista de dependências pip
├─ MetalSense_Documentacao.html   # Versão HTML gerada anteriormente
└─ README.md                # Visão geral do projeto
```

### 5.2 README – Escopo do Projeto
```markdown
# MetalSense – Monitoramento Inteligente de Máquinas Industriais

## Visão geral
MetalSense é um protótipo de sistema de monitoramento que captura parâmetros operacionais (temperatura, corrente, vibração, tempo de operação) de máquinas industriais e identifica anomalias a partir do histórico de dados. A aplicação demonstra a integração de IoT, análise de dados e UI para manutenção preditiva.

## Funcionalidades principais
- Simulação de sensores que enviam leituras a cada 5 s.
- Servidor Python que persiste as leituras em SQLite.
- Detector de anomalias baseado em desvio percentual.
- Interface gráfica (PyQt5) com gráficos em tempo real, tabela de histórico filtrável e painel de alertas.
- Exportação de histórico em CSV.
- Estrutura modular que permite substituir o simulador por hardware real.

## Como executar
```powershell
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor
python src/server.py

# 4. Abra a UI
python ui/main_window.py
```

## Contribuição
1. Fork o repositório.
2. Crie uma branch (`git checkout -b feature/<nome>`).
3. Commit as alterações (`git commit -m "descrição"`).
4. Push e abra Pull Request.

## Licença
MIT – veja o arquivo `LICENSE` para detalhes.

## Contato da equipe
E‑mail: techforge2024@escola.edu.br
Telegram: @TechForge_MetalSense
```

### 5.3 Controle de Versão (últimos commits)
| SHA | Data | Mensagem |
|-----|------|----------|
| `a7c9f2b` | 2024‑08‑12 | Implementação inicial do detector de anomalias |
| `d3e5a1c` | 2024‑09‑03 | Adicionar exportação CSV e testes unitários |
| `9b2f8e4` | 2025‑02‑15 | Refatorar UI: inclusão de painel de alertas |
| `4c1d7a9` | 2025‑06‑22 | Migrar banco para SQLite, criar script de backup |
| `e0f3b6d` | 2026‑03‑10 | Atualizar README e diagramas Mermaid |
| `f4a2d9e` | 2026‑09‑05 | Melhorias na detecção de anomalias (threshold dinâmico) |

---

## ANEXOS (para facilitar a revisão)
### A. Lista de dependências (`requirements.txt`)
```
beautifulsoup4==4.15.0
lxml==6.1.3
python-docx==1.2.0
requests==2.34.2
pandas==2.2.1
scikit-learn==1.5.0
pyqt5==5.15.9
```

### B. Instruções para gerar a documentação em PDF/Word
1. Instalar as dependências listadas acima.
2. Executar o script `generate_docx.py` que converte `MetalSense_Documentacao.html` em `MetalSense_Documentacao_Final.docx`.
3. Abrir o `.docx` no Microsoft Word e, se desejar, salvar como PDF.

### C. Possíveis extensões futuras
- **Sensores reais:** substituir o simulador por hardware (Arduino, ESP32) via MQTT.
- **ML avançado:** utilizar Isolation Forest ou LSTM para detecção de anomalias mais sofisticada.
- **Dashboard web:** migrar a UI para Flask/Django + Chart.js, permitindo acesso remoto.
- **Persistência na nuvem:** usar PostgreSQL em AWS RDS ou Cloud SQL; backups automáticos.
- **CI/CD:** GitHub Actions para testes automatizados, linting e geração de artefatos de documentação a cada push.

---

*Fim da documentação.*
