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
