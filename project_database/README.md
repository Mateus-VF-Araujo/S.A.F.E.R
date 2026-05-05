# Banco de dados do projeto

O banco de dados relacional (SQLite) é gerenciado pelo SQLAlchemy e possui três tabelas principais. A tabela de pessoa comum atua como a base central, com as outras tabelas estendendo suas informações através da chave primária/estrangeira (`cpf`).

### Tabela `common_person` (Pessoa Comum)
Armazena a biometria e os dados civis básicos de todas as pessoas cadastradas.
*   **`cpf`** *(String, Primary Key)*: Identificador único e chave primária.
*   **`full_name`** *(String)*: Nome completo da pessoa.
*   **`mother_full_name`** *(String)*: Nome completo da mãe da pessoa.
*   **`birth_date`** *(Date)*: Data de nascimento.
*   **`is_wanted`** *(Boolean)*: Flag indicando se a pessoa é procurada pela justiça/segurança.
*   **`is_employee`** *(Boolean)*: Flag indicando se a pessoa é um funcionário com acesso de admin.
*   **`encoding`** *(LargeBinary)*: O vetor matemático de 128 dimensões da biometria facial.

### Tabela `wanted` (Alvos/Procurados)
Armazena os detalhes dos alertas para pessoas marcadas como procuradas.
*   **`cpf`** *(String, Primary Key / Foreign Key)*: Chave vinculada à tabela `common_person`.
*   **`crime`** *(String)*: O crime ou motivo da busca (ex: Mandado em aberto, Suspeito).
*   **`risk_level`** *(String)*: Classificação do nível de risco da pessoa (ex: ALTO, BAIXO).

### Tabela `employee` (Funcionários)
Tabela de extensão para pessoas que possuem acesso de administrador no sistema.
*   **`cpf`** *(String, Primary Key / Foreign Key)*: Chave vinculada à tabela `common_person`.
