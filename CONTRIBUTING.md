# Contribuindo com o MetalSense

Este documento reúne as regras e convenções que o time TechForge segue no desenvolvimento do MetalSense. O objetivo é manter o projeto organizado e fácil de entender pra qualquer pessoa do grupo.

## Padrão de commits

Usamos prefixos nas mensagens de commit pra deixar claro o tipo de mudança:

- `feat:` — nova funcionalidade
- `fix:` — correção de bug
- `refactor:` — reorganização do código sem mudar o comportamento
- `chore:` — manutenção geral (configs, limpeza, dependências)
- `docs:` — mudanças em documentação
- `style:` — formatação/estilo do código (sem afetar funcionamento)
- `test:` — testes automatizados

Exemplo: `feat: adiciona registro de medicao no historico`

## Fluxo de branches

- A `main` é a branch estável do projeto — só recebe código já testado e funcionando.
- Toda nova funcionalidade, correção ou refatoração deve ser feita em uma branch separada, criada a partir da `main`.
- Só faça merge na `main` depois de testar que tudo funciona.
- Nomeie a branch de forma descritiva (ex: `refatorar-logica`, `ui-streamlit`), evitando nomes genéricos.

## Organização dos módulos

O projeto é dividido por responsabilidade:

- `main.py` — fluxo principal / entrada do sistema (menu, chamadas às funções)
- `dados.py` — persistência dos dados (carregar e salvar o JSON)
- `maquinas.py` — lógica relacionada às máquinas (cadastro, remoção, medições, análise)

Antes de criar um módulo novo, avalie se ele realmente representa uma responsabilidade diferente das já existentes — evite dividir o projeto sem necessidade.

## Separação entre lógica e interação

Dentro de `maquinas.py`, cada funcionalidade é dividida em duas partes:

- **Função de lógica pura**: recebe os dados já prontos como parâmetro, processa e retorna um resultado. Nunca usa `input()` ou `print()`.
- **Função de interação (CLI)**: usa `input()` para coletar dados do usuário e `print()` para mostrar mensagens, delegando o processamento para a função de lógica correspondente.

Essa separação existe porque a lógica precisa ser reaproveitável tanto pelo terminal quanto pela interface gráfica (Streamlit), sem duplicar código.

Exemplo:

```python
# lógica pura
def criar_maquina(dados, nome_da_maquina):
    ...
    return nova_maquina

# interação (CLI)
def cadastrar_maquina(dados):
    nome_da_maquina =
