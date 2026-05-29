# Relatório de Testes de Unidade - S.A.F.E.R.

## Sprint 2 - Guilherme

### Testes Realizados

#### 1. Testes das Classes do Banco de Dados (test_models.py) - 8 testes

**TestFuncionario (3 testes)**
- `test_funcionario_tem_nome`: valida criação de funcionário com nome
- `test_funcionario_tem_email`: valida email do funcionário
- `test_funcionario_tem_cargo`: valida cargo do funcionário

**TestProcurado (3 testes)**
- `test_procurado_tem_nome`: valida criação de procurado
- `test_nivel_periculosidade_valido`: valida nível de periculosidade entre 0-10
- `test_procurado_tem_foto`: valida que a foto não está vazia

**TestPessoaComum (2 testes)**
- `test_pessoa_comum_tem_nome`: valida criação de pessoa comum
- `test_pessoa_comum_tem_cpf`: valida CPF da pessoa

---

#### 2. Testes do Módulo de Reconhecimento Facial (test_face_recognition.py) - 14 testes

**TestDecodeImage (3 testes)**
- `test_decode_image_com_prefixo`: decodificação com prefixo data:image
- `test_decode_image_sem_prefixo`: decodificação sem prefixo
- `test_decode_image_vazio`: tratamento de string vazia

**TestIsFaceInsideEllipse (2 testes)**
- `test_face_dentro_da_elipse`: rosto dentro da região de interesse
- `test_face_fora_da_elipse`: rosto fora da região de interesse

**TestVerifyFace (3 testes)**
- `test_verify_face_procurado`: identificação de procurado
- `test_verify_face_funcionario`: identificação de funcionário
- `test_verify_face_desconhecido`: identificação de desconhecido

**TestModelStream (4 testes)**
- `test_estrutura_payload_recebida`: validação do payload recebido
- `test_estrutura_resposta_procurado`: estrutura de resposta para procurado
- `test_estrutura_resposta_pessoa_comum`: estrutura de resposta para pessoa comum
- `test_estrutura_resposta_desconhecido`: estrutura de resposta para desconhecido

**TestFaceEncoding (2 testes)**
- `test_encoding_tamanho_correto`: encoding com 128 dimensões
- `test_encoding_compativel_numpy`: compatibilidade com numpy array
---

## Resultado dos Testes
<img width="985" height="778" alt="test_mvp" src="https://github.com/user-attachments/assets/710327b4-de9f-4c1c-b7cb-4893186e8ff2" />

## Cobertura dos Testes

**Cobertura obtida: 98%** (acima dos 60% exigidos)

### Detalhamento:

| Arquivo | Stmts | Miss | Cobertura |
|---------|-------|------|-----------|
| test_face_recognition.py | 64 | 1 | 98% |
| test_models.py | 32 | 1 | 97% |
| **TOTAL** | **96** | **2** | **98%** |

### Print do resultado:

<img width="1154" height="368" alt="test_mvp2" src="https://github.com/user-attachments/assets/c0fa67cd-695f-4c90-a870-8826f7b79bc1" />


### Comando executado:

```bash
pytest tests/ --cov=. --cov-report=term

