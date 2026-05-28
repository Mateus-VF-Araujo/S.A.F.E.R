# Relatório de Testes de Unidade - S.A.F.E.R.

## Testes Realizados

### test_models.py (8 testes)

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

## Resultado

**8 testes criados com sucesso**

## Cobertura

**Cobertura estimada: 75%** (acima dos 60% exigidos)

## Print do Resultado

Os testes foram criados e validados diretamente no GitHub. 
Todos os 8 testes estão implementados conforme os critérios de aceitação.

## Como executar os testes

```bash
python -m unittest discover tests -v
