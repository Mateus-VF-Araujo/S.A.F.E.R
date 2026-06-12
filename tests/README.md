# Testes automatizados

Esta pasta contém os testes automatizados do projeto S.A.F.E.R. Eles foram criados com `pytest` e `pytest-cov` para validar partes importantes do sistema e também gerar o percentual de cobertura de código.

Para rodar localmente:

```powershell
uv run pytest
```

Esse comando executa todos os testes e mostra a cobertura no final da saída do terminal.

## Estrutura

- `conftest.py`: configura o caminho raiz do projeto para que os imports como `database.functions` e `facial.model_stream` funcionem corretamente durante os testes.
- `test_database_functions.py`: testa funções de validação, Base64, criação de modelos e persistência simulada.
- `test_facial_modules.py`: testa regras unitárias dos módulos de reconhecimento facial sem depender de banco real, câmera ou reconhecimento facial pesado.

## Testes de `database.functions`

O arquivo `test_database_functions.py` cobre funções usadas para preparar dados antes de salvar no banco.

### Base64 e imagens

Foram criados testes para:

- `remover_prefixo_base64`: garante que uma string Base64 pura permanece igual.
- `remover_prefixo_base64`: garante que uma data URL como `data:image/png;base64,...` tem o prefixo removido.
- `codificar_imagem_para_base64`: valida que uma imagem pequena salva em disco e convertida para Base64 retorna o conteúdo esperado.
- `decodificar_imagem_base64`: valida que o Base64 gerado pode ser aberto novamente pelo OpenCV.
- `validar_foto_base64`: garante que uma imagem válida retorna o Base64 limpo, sem prefixo.
- `validar_foto_base64`: garante que um conteúdo Base64 que não representa imagem gera `ValueError`.

Esses testes usam uma imagem pequena criada em memória com `numpy` e codificada com `cv2.imencode`, para evitar depender de arquivos externos.

### Validação de campos

Também foram testadas as validações:

- `validar_campos_modelo`: rejeita campos que não existem no modelo SQLAlchemy.
- `validar_campos_obrigatorios`: rejeita campos ausentes, vazios ou `None`.

Esses testes ajudam a garantir que dados inválidos sejam barrados antes de criar objetos do banco.

### Criação de registros

Foram testadas as funções:

- `criar_funcionario`
- `criar_procurado`
- `criar_pessoa_comum`

Para isso foi usada uma classe `FakeSession`, que simula os métodos principais de uma sessão SQLAlchemy:

- `add`
- `commit`
- `refresh`

Assim os testes verificam se os objetos são criados corretamente sem precisar conectar em um banco MySQL real.

Nos casos de `criar_procurado` e `criar_pessoa_comum`, os testes também verificam se:

- o `cadastrado_por` é preenchido com o ID recebido;
- a foto em Base64 é validada;
- o prefixo `data:image/...;base64,` é removido quando existe.

## Testes de `facial.access_database`

O arquivo `test_facial_modules.py` testa a função `verify_face` do módulo `facial.access_database`.

Foram cobertos estes cenários:

- quando o banco biométrico está vazio, a função retorna `{"status": "unknown"}`;
- quando existe um match facial válido, a função retorna os metadados da pessoa encontrada;
- quando existe distância calculada, mas o melhor resultado não é confirmado por `compare_faces`, a função retorna `{"status": "unknown"}`.

Esses testes usam `monkeypatch` para simular chamadas externas:

- `carregar_banco_biometrico`
- `face_recognition.compare_faces`
- `face_recognition.face_distance`

Isso permite testar a regra de decisão da função sem rodar reconhecimento facial real.

## Testes de `facial.model_stream`

O mesmo arquivo também cobre funções menores de `facial.model_stream`.

Foram testados:

- `decode_image`: garante que uma imagem enviada como data URL Base64 é decodificada corretamente.
- `is_face_inside_ellipse`: valida quando uma caixa de rosto está dentro ou fora da elipse esperada.
- `analisar_foto_streamlit`: garante que bytes inválidos retornam uma lista vazia, em vez de quebrar a aplicação.
- `get_estatisticas`: simula uma sessão de banco e verifica se procurados, pessoas comuns e funcionários são agregados no formato esperado.

No teste de `get_estatisticas`, o banco também é simulado com classes falsas para evitar depender de MySQL no ambiente de CI.

## Por que a cobertura de `access_database.py` ficou baixa?

A cobertura de `facial/access_database.py` ficou mais baixa porque a maior parte do arquivo está dentro da função `carregar_banco_biometrico`.

Essa função faz várias operações pesadas e dependentes de ambiente:

- abre conexão com banco de dados;
- consulta tabelas de `Procurado` e `PessoaComum`;
- percorre registros vindos do banco;
- valida tamanho de fotos;
- decodifica imagens Base64;
- redimensiona imagens com OpenCV;
- converte imagens de BGR para RGB;
- chama `face_recognition.face_encodings`;
- trata imagens corrompidas;
- fecha a sessão do banco.

Para manter o CI estável, os testes atuais evitam depender de:

- MySQL rodando;
- banco populado;
- câmera;
- imagens reais grandes;
- processamento real de reconhecimento facial;
- comportamento nativo do `dlib` em tempo de teste.

Por isso, os testes de `access_database.py` focam principalmente em `verify_face`, que é a regra de decisão mais fácil de testar de forma isolada.

## Como aumentar essa cobertura no futuro

O melhor caminho para aumentar a cobertura de `access_database.py` é dividir `carregar_banco_biometrico` em funções menores.

Exemplos de funções que poderiam ser extraídas:

```python
def deve_ignorar_foto(foto_base64):
    ...

def preparar_imagem_para_face_recognition(foto_base64):
    ...

def criar_metadata_procurado(procurado):
    ...

def criar_metadata_pessoa_comum(pessoa):
    ...

def extrair_primeiro_encoding(imagem_rgb):
    ...
```

Com essa separação, seria possível testar cada parte isoladamente com imagens pequenas e mocks simples. A cobertura aumentaria sem tornar os testes lentos ou dependentes de banco real.

## CI

O workflow do GitHub Actions fica em:

```text
.github/workflows/ci.yml
```

Ele roda automaticamente em:

- pull requests para a branch `main`;
- push direto na branch `main`.

O CI executa:

```powershell
uv sync --dev --locked
uv run pytest
```

Como o projeto usa um wheel local de `dlib` para Windows, o workflow roda em `windows-latest`.

Ao final, o `pytest-cov` mostra a porcentagem de cobertura no terminal e gera o arquivo `coverage.xml`, que é enviado como artifact do GitHub Actions.
