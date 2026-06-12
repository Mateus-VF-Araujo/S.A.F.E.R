import base64

import cv2
import numpy as np
import pytest

from database.functions import (
    codificar_imagem_para_base64,
    criar_funcionario,
    criar_pessoa_comum,
    criar_procurado,
    decodificar_imagem_base64,
    remover_prefixo_base64,
    validar_campos_modelo,
    validar_campos_obrigatorios,
    validar_foto_base64,
)
from database.models import Funcionario, PessoaComum, Procurado


class FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.refreshed = []

    def add(self, instance):
        self.added.append(instance)

    def commit(self):
        self.commits += 1

    def refresh(self, instance):
        self.refreshed.append(instance)


@pytest.fixture
def imagem_base64():
    imagem = np.zeros((2, 3, 3), dtype=np.uint8)
    imagem[:, :] = [10, 20, 30]
    ok, buffer = cv2.imencode(".png", imagem)
    assert ok
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def test_remover_prefixo_base64_preserva_string_sem_data_url(imagem_base64):
    assert remover_prefixo_base64(imagem_base64) == imagem_base64


def test_remover_prefixo_base64_remove_data_url(imagem_base64):
    data_url = f"data:image/png;base64,{imagem_base64}"

    assert remover_prefixo_base64(data_url) == imagem_base64


def test_codificar_e_decodificar_imagem_base64(tmp_path, imagem_base64):
    caminho = tmp_path / "foto.png"
    caminho.write_bytes(base64.b64decode(imagem_base64))

    codificada = codificar_imagem_para_base64(caminho)
    decodificada = decodificar_imagem_base64(codificada)

    assert codificada == imagem_base64
    assert decodificada.shape == (2, 3, 3)


def test_validar_foto_base64_retorna_base64_sem_prefixo(imagem_base64):
    data_url = f"data:image/png;base64,{imagem_base64}"

    assert validar_foto_base64(data_url) == imagem_base64


def test_validar_foto_base64_rejeita_conteudo_que_nao_e_imagem():
    texto_base64 = base64.b64encode(b"nao e uma imagem").decode("utf-8")

    with pytest.raises(ValueError, match="nao pode ser decodificada"):
        validar_foto_base64(texto_base64)


def test_validar_campos_modelo_rejeita_campo_inexistente():
    with pytest.raises(ValueError, match="Campos invalidos para Funcionario: apelido"):
        validar_campos_modelo(Funcionario, {"nome": "Ana", "apelido": "A"})


def test_validar_campos_obrigatorios_rejeita_ausentes_e_vazios():
    with pytest.raises(ValueError, match="Campos obrigatorios ausentes: cargo, nome"):
        validar_campos_obrigatorios({"nome": "", "email": "a@b.com"}, ["nome", "cargo"])


def test_criar_funcionario_persiste_instancia_com_dados_validos():
    session = FakeSession()
    dados = {
        "nome": "Mateus",
        "cargo": "Analista",
        "cpf": "123.456.789-00",
        "nivel_acesso": 2,
        "email": "mateus@example.com",
        "senha_hash": "hash",
    }

    funcionario = criar_funcionario(session, dados)

    assert isinstance(funcionario, Funcionario)
    assert funcionario.nome == "Mateus"
    assert session.added == [funcionario]
    assert session.commits == 1
    assert session.refreshed == [funcionario]


def test_criar_procurado_vincula_cadastrador_e_valida_foto(imagem_base64):
    session = FakeSession()
    dados = {
        "nome": "Pessoa Procurada",
        "cpf": "111.222.333-44",
        "nivel_periculosidade": 4,
        "foto_base64": f"data:image/png;base64,{imagem_base64}",
    }

    procurado = criar_procurado(session, dados, cadastrador_id=7)

    assert isinstance(procurado, Procurado)
    assert procurado.cadastrado_por == 7
    assert procurado.foto_base64 == imagem_base64
    assert session.added == [procurado]


def test_criar_pessoa_comum_vincula_cadastrador_e_valida_foto(imagem_base64):
    session = FakeSession()
    dados = {
        "nome": "Pessoa Monitorada",
        "cpf": "555.666.777-88",
        "foto_base64": imagem_base64,
    }

    pessoa = criar_pessoa_comum(session, dados, cadastrador_id=3)

    assert isinstance(pessoa, PessoaComum)
    assert pessoa.cadastrado_por == 3
    assert pessoa.foto_base64 == imagem_base64
    assert session.added == [pessoa]
