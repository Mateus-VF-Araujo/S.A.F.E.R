<p align="center">
  <img src="../assets/safer-database-banner.svg" alt="Banner do banco de dados do S.A.F.E.R." width="100%">
</p>

# Tutorial do Banco de Dados

Este diretório reúne os arquivos responsáveis pela conexão, criação e alimentação do banco de dados usado pelo projeto S.A.F.E.R.

O script principal para iniciar a estrutura do banco é o `database.py`. Antes de executá-lo, é necessário preparar o MySQL localmente.

## Pré-requisitos

Antes de rodar o script, verifique se:

- O MySQL está instalado.
- O servidor MySQL está em execução.
- O banco de dados `safer_db` já foi criado.
- As dependências do projeto foram instaladas, incluindo `sqlalchemy` e `pymysql`.

## Criando o banco de dados

O banco pode ser criado por um cliente MySQL, como MySQL Workbench, DBeaver ou phpMyAdmin.

Também é possível criar pela linha de comando:

```bash
mysql -u usuario -p -e "CREATE DATABASE safer_db;"
```

Substitua `usuario` pelo seu usuário local do MySQL. Após executar o comando, a senha será solicitada no terminal.

## Configurando a conexão

No arquivo `database.py`, existe uma variável chamada `DATABASE_URL`:

```python
DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/safer_db"
```

Essa URL informa ao SQLAlchemy como acessar o banco. Substitua os valores de exemplo pelos dados do seu ambiente:

- `usuario`: usuário do MySQL.
- `senha`: senha do MySQL.
- `localhost`: endereço do servidor MySQL.
- `3306`: porta usada pelo MySQL.
- `safer_db`: nome do banco de dados.

Exemplo:

```python
DATABASE_URL = "mysql+pymysql://root:minhasenha@localhost:3306/safer_db"
```

## Criando as tabelas

Depois de configurar a conexão, execute o script:

```bash
python database/database.py
```

Ao executar esse comando, a função `init_db()` será chamada. Ela usa os modelos definidos em `models.py` para criar, no MySQL, as tabelas mapeadas pelas classes que herdam de `Base`.

Se tudo estiver configurado corretamente, a mensagem abaixo será exibida:

```text
Tabelas criadas com sucesso!
```

## Importando os dados públicos

Depois que o banco estiver criado, o arquivo `databaseDadosPublicos.py` pode ser usado para carregar os dados do arquivo `BancoVDE2025.csv` no MySQL.

Esse script faz as seguintes etapas:

- Lê o arquivo `BancoVDE2025.csv` com `pandas`.
- Filtra os registros da UF `RN`.
- Trata colunas numéricas, preenchendo valores vazios com `0`.
- Trata colunas de texto, preenchendo valores vazios com `NÃO INFORMADO`.
- Converte a coluna `data_referencia` para o formato aceito pelo banco.
- Envia os dados tratados para a tabela `dados_seguranca_publica`.

Antes de rodar o script, confira a variável `DATABASE_URL` dentro de `databaseDadosPublicos.py`:

```python
DATABASE_URL = "mysql+pymysql://usuario:senha@localhost/safer_db"
```

Substitua `usuario`, `senha`, `host` e o nome do banco pelos dados do seu ambiente local.

Também confira se o caminho do arquivo CSV está correto:

```python
caminho_do_arquivo = r"C:\dev\S.A.F.E.R\database\BancoVDE2025.csv"
```

Se o projeto estiver em outra pasta, ajuste esse caminho antes da execução.

Para importar os dados públicos, execute:

```bash
python database/databaseDadosPublicos.py
```

Durante a execução, o script exibirá mensagens indicando o início do processo, o envio para o banco e o fim da importação.

> Observação: o script usa `if_exists='replace'`, então a tabela `dados_seguranca_publica` será substituída caso já exista.

## Arquivos principais

- `database.py`: configura a conexão com o MySQL e cria as tabelas do banco.
- `models.py`: define os modelos e a estrutura das tabelas.
- `functions.py`: reúne funções auxiliares relacionadas ao banco.
- `databaseDadosPublicos.py`: importa dados públicos do arquivo CSV para o banco.
- `BancoVDE2025.csv`: base de dados pública usada no processo de importação.

## Observações

Se ocorrer erro de conexão, confira se o MySQL está rodando, se o banco `safer_db` existe e se os dados da `DATABASE_URL` estão corretos.

Caso o script seja executado fora da raiz do projeto, pode ser necessário ajustar o caminho ou rodar o comando a partir da pasta principal do repositório.
