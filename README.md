# MetalSense

Sistema inteligente para detecção e previsão de anomalias em máquinas industriais.

## Sobre o projeto

O **MetalSense** é um projeto desenvolvido pelo grupo **TechForge** no curso Técnico em Desenvolvimento de Sistemas.

O sistema tem como objetivo auxiliar na identificação de comportamentos anormais em máquinas industriais, utilizando dados de operação para construir um histórico e identificar alterações que possam indicar uma possível falha ou necessidade de manutenção.

A proposta é utilizar tecnologia para transformar dados das máquinas em informações que possam ajudar na prevenção de paradas inesperadas.

## Problema

Alterações no funcionamento de máquinas podem passar despercebidas até que provoquem uma falha ou uma parada inesperada na produção.

O MetalSense busca identificar essas alterações com antecedência, analisando o comportamento das máquinas ao longo do tempo.

## Objetivo

Desenvolver um sistema capaz de:

* Cadastrar e identificar máquinas;
* Registrar dados de funcionamento;
* Armazenar um histórico de operação;
* Analisar o comportamento individual de cada máquina;
* Detectar possíveis anomalias;
* Auxiliar na identificação de possíveis falhas antes que ocorram;
* Apresentar as informações de forma clara para o usuário.

## Tecnologias

* **Python** — desenvolvimento do sistema e processamento dos dados;
* **JSON / Banco de dados** — armazenamento das informações;
* **Streamlit** — interface gráfica e visualização dos dados;
* **Machine Learning** — análise e previsão de possíveis anomalias;
* **IoT** — coleta de dados diretamente das máquinas.

## Funcionamento previsto

O funcionamento do MetalSense seguirá, de forma geral, o seguinte fluxo:

```text
Máquina / Sensores
       ↓
Coleta de dados
       ↓
MetalSense
       ↓
Armazenamento do histórico
       ↓
Análise dos dados
       ↓
Detecção de anomalias
       ↓
Identificação de possíveis problemas
       ↓
Visualização no sistema
```

## Diferencial

O sistema não pretende utilizar somente limites fixos para determinar se uma máquina está funcionando corretamente.

O MetalSense busca analisar o **comportamento individual de cada máquina**, permitindo identificar mudanças em relação ao seu próprio histórico de funcionamento.

## Estrutura atual

O projeto encontra-se em desenvolvimento e sua estrutura será organizada conforme novas funcionalidades forem implementadas.

Atualmente, o sistema possui funcionalidades relacionadas ao cadastro, consulta e remoção de máquinas, além do armazenamento das informações em arquivo JSON.

## Equipe

**TechForge**

Projeto desenvolvido como parte do curso Técnico em Desenvolvimento de Sistemas.

## Status

🚧 **Em desenvolvimento**

Novas funcionalidades de coleta de dados, histórico, análise de anomalias, Machine Learning, IoT e interface gráfica serão adicionadas durante o desenvolvimento do projeto.
