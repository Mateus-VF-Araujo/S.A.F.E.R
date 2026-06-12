<p align="center">
  <img src="assets/safer-banner_of.svg" alt="Banner do software S.A.F.E.R." width="100%">
</p>

# S.A.F.E.R.

Repositório do projeto **S.A.F.E.R. - Sistema de Análise Facial para Entidades de Risco**, uma aplicação em Python voltada para reconhecimento facial, consulta de pessoas cadastradas e análise de dados públicos de segurança.

O sistema usa **Streamlit** para a interface, **MySQL** para persistência dos dados, **SQLAlchemy** para modelagem do banco, **OpenCV/face-recognition** para processamento facial e **Plotly/Pandas** para visualização de dados.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do Banco](#configuração-do-banco)
- [Como Executar](#como-executar)
- [Testes e Cobertura](#testes-e-cobertura)
- [CI](#ci)
- [Fonte dos Dados](#fonte-dos-dados)
- [Equipe](#equipe)
- [Licença](#licença)

## Sobre o Projeto

O S.A.F.E.R. foi desenvolvido para apoiar fluxos de monitoramento e consulta em um ambiente de segurança. A aplicação permite autenticar funcionários, controlar permissões por nível de acesso, gerenciar registros internos, consultar pessoas procuradas e analisar dados públicos de segurança.

O projeto também possui um módulo de reconhecimento facial que compara uma imagem capturada pela câmera com registros biométricos armazenados no banco.

## Funcionalidades

- Login de funcionários por CPF ou e-mail.
- Controle de acesso por nível de permissão.
- Dashboard operacional em Streamlit.
- Câmera de reconhecimento facial via `st.camera_input`.
- Consulta de pessoas procuradas por nome ou CPF.
- CRUD de funcionários, procurados e pessoas comuns.
- Cadastro de fotos em Base64.
- Análise de dados públicos de segurança com gráficos e filtros.
- Criação de view SQL para resumo de cadastros.
- Testes automatizados com relatório de cobertura.
- CI no GitHub Actions para rodar testes em PRs e merges na `main`.

## Tecnologias

- Python 3.10
- Streamlit
- SQLAlchemy
- MySQL / PyMySQL
- Pandas
- Plotly
- OpenCV
- dlib
- face-recognition
- pytest
- pytest-cov
- uv

## Estrutura do Projeto

```text
S.A.F.E.R/
+-- .github/
|   +-- workflows/
|       +-- ci.yml
+-- assets/
|   +-- safer-banner.svg
|   +-- safer-database-banner.svg
+-- dashconfig/
|   +-- estilo.py
|   +-- funtionsDash.py
+-- database/
|   +-- fotosProcurados/
|   +-- BancoVDE2025.csv
|   +-- database.py
|   +-- databaseDadosPublicos.py
|   +-- functions.py
|   +-- models.py
|   +-- populationData.py
|   +-- README.md
+-- facial/
|   +-- utils/
|   |   +-- dlib-19.22.99-cp310-cp310-win_amd64.whl
|   +-- access_database.py
|   +-- model_stream.py
+-- tests/
|   +-- conftest.py
|   +-- README.md
|   +-- test_database_functions.py
|   +-- test_facial_modules.py
+-- dashboardStreamlit.py
+-- pyproject.toml
+-- uv.lock
+-- README.md
+-- LICENSE
```

### Principais pastas e arquivos

- `dashboardStreamlit.py`: ponto de entrada da aplicação Streamlit.
- `dashconfig/`: funções e estilos usados pelo dashboard.
- `database/`: modelos, conexão, scripts de criação/população e dados públicos.
- `facial/`: lógica de reconhecimento facial e acesso ao banco biométrico.
- `tests/`: testes automatizados e documentação dos testes.
- `.github/workflows/ci.yml`: workflow de CI para execução automática dos testes.
- `pyproject.toml`: dependências e configurações do projeto.
- `uv.lock`: lockfile das dependências gerenciado pelo `uv`.

## Pré-requisitos

Antes de rodar o projeto, tenha instalado:

- Python 3.10
- uv
- MySQL
- Git

O projeto usa um wheel local de `dlib` para Windows:

```text
facial/utils/dlib-19.22.99-cp310-cp310-win_amd64.whl
```

Por isso, o ambiente mais direto para executar o projeto é Windows com Python 3.10.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/Mateus-VF-Araujo/S.A.F.E.R.git
cd S.A.F.E.R
```

Instale as dependências:

```bash
uv sync --dev
```

Se quiser instalar apenas as dependências de execução, sem ferramentas de teste:

```bash
uv sync
```

## Configuração do Banco

Crie o banco MySQL local:

```sql
CREATE DATABASE safer_db;
```

Por padrão, alguns módulos usam a conexão:

```text
mysql+pymysql://root:root@localhost:3306/safer_db
```

Se o seu usuário, senha, host ou porta forem diferentes, ajuste a conexão nos arquivos:

- `database/database.py`
- `database/databaseDadosPublicos.py`

O dashboard também aceita a variável de ambiente `SAFER_DATABASE_URL`:

```powershell
$env:SAFER_DATABASE_URL="mysql+pymysql://usuario:senha@localhost:3306/safer_db"
```

Crie as tabelas:

```bash
uv run python database/database.py
```

Popule o banco com dados iniciais de exemplo:

```bash
uv run python database/populationData.py
```

Para importar os dados públicos do CSV para a tabela `dados_seguranca_publica`, confira antes o caminho do arquivo em `database/databaseDadosPublicos.py` e execute:

```bash
uv run python database/databaseDadosPublicos.py
```

Mais detalhes sobre o banco estão em [database/README.md](database/README.md).

## Como Executar

Inicie o dashboard:

```bash
uv run streamlit run dashboardStreamlit.py
```

Depois, acesse o endereço exibido pelo Streamlit no terminal.

### Usuários iniciais

O script `database/populationData.py` cria funcionários de exemplo. Alguns logins cadastrados são:

```text
E-mail: joaomachado@safer.local
Senha: joaomachado123

E-mail: mariasilva@safer.local
Senha: mariasilva123
```

Também é possível fazer login pelo CPF cadastrado.

## Testes e Cobertura

Os testes ficam na pasta `tests/` e usam `pytest` com `pytest-cov`.

Para rodar:

```bash
uv run pytest
```

O comando mostra a porcentagem de cobertura no terminal e gera o arquivo `coverage.xml`.

A documentação detalhada dos testes está em [tests/README.md](tests/README.md).

## CI

O projeto possui CI configurado em:

```text
.github/workflows/ci.yml
```

O workflow roda automaticamente em:

- pull requests para a branch `main`;
- pushes na branch `main`.

O CI executa:

```bash
uv sync --dev --locked
uv run pytest
```

Como o projeto depende do wheel local de `dlib` para Windows, o workflow usa `windows-latest`.

## Fonte dos Dados

A base pública utilizada no projeto foi obtida no portal do Ministério da Justiça e Segurança Pública:

[Base de Dados e Notas Metodológicas dos Gestores Estaduais - Sinesp VDE 2015 a 2026](https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/dados-nacionais-1/base-de-dados-e-notas-metodologicas-dos-gestores-estaduais-sinesp-vde-2022-e-2023)

O arquivo original foi disponibilizado em `.xlsx`. Para uso no projeto, ele foi convertido para `.csv` e salvo em:

```text
database/BancoVDE2025.csv
```

## Equipe

- Kennymar Bezerra de Oliveira
- Guilherme Souza de Farias
- Soraia Pereira de Araújo
- Mateus Vinicius Figueredo de Araújo

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
