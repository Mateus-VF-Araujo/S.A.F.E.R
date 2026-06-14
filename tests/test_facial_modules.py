import base64
from types import SimpleNamespace

import cv2
import numpy as np

from facial import access_database, model_stream


def test_verify_face_retorna_unknown_quando_banco_biometrico_vazio(monkeypatch):
    monkeypatch.setattr(access_database, "carregar_banco_biometrico", lambda: ([], []))

    assert access_database.verify_face([0.1, 0.2]) == {"status": "unknown"}


def test_verify_face_retorna_metadata_do_melhor_match(monkeypatch):
    conhecido_1 = np.array([0.0, 0.0])
    conhecido_2 = np.array([1.0, 1.0])
    metadata = [
        {"status": "common_cleared", "full_name": "Pessoa comum"},
        {"status": "wanted_alert", "full_name": "Pessoa procurada"},
    ]

    monkeypatch.setattr(
        access_database,
        "carregar_banco_biometrico",
        lambda: ([conhecido_1, conhecido_2], metadata),
    )
    monkeypatch.setattr(
        access_database.face_recognition,
        "compare_faces",
        lambda known, target, tolerance: [False, True],
    )
    monkeypatch.setattr(
        access_database.face_recognition,
        "face_distance",
        lambda known, target: np.array([0.8, 0.2]),
    )

    assert access_database.verify_face([1.0, 1.0]) == metadata[1]


def test_verify_face_retorna_unknown_quando_melhor_distancia_nao_confere(monkeypatch):
    metadata = [{"status": "common_cleared", "full_name": "Pessoa comum"}]

    monkeypatch.setattr(
        access_database,
        "carregar_banco_biometrico",
        lambda: ([np.array([0.0, 0.0])], metadata),
    )
    monkeypatch.setattr(
        access_database.face_recognition,
        "compare_faces",
        lambda known, target, tolerance: [False],
    )
    monkeypatch.setattr(
        access_database.face_recognition,
        "face_distance",
        lambda known, target: np.array([0.9]),
    )

    assert access_database.verify_face([1.0, 1.0]) == {"status": "unknown"}


def test_decode_image_aceita_data_url():
    imagem = np.zeros((4, 5, 3), dtype=np.uint8)
    ok, buffer = cv2.imencode(".png", imagem)
    assert ok
    payload = base64.b64encode(buffer.tobytes()).decode("utf-8")

    decodificada = model_stream.decode_image(f"data:image/png;base64,{payload}")

    assert decodificada.shape == (4, 5, 3)


def test_is_face_inside_ellipse_valida_todos_os_cantos():
    center = (50, 50)
    axes = (40, 30)

    assert model_stream.is_face_inside_ellipse(40, 60, 55, 45, center, axes)
    assert not model_stream.is_face_inside_ellipse(5, 95, 35, 65, center, axes)


def test_analisar_foto_streamlit_retorna_lista_vazia_para_bytes_invalidos():
    assert model_stream.analisar_foto_streamlit(b"conteudo invalido") == []


def test_get_estatisticas_agrega_procurados_comuns_e_funcionarios(monkeypatch):
    procurado = SimpleNamespace(
        id=1,
        nome="Procurado",
        cpf="111",
        foto_base64="foto-p",
    )
    comum = SimpleNamespace(
        id=2,
        nome="Monitorado",
        cpf="222",
        foto_base64="foto-c",
    )
    funcionario = SimpleNamespace(
        id=3,
        nome="Funcionario",
        cpf="333",
    )

    class Query:
        def __init__(self, items):
            self.items = items

        def all(self):
            return self.items

    class FakeDb:
        def __init__(self):
            self.closed = False

        def query(self, model):
            if model is model_stream.Procurado:
                return Query([procurado])
            if model is model_stream.PessoaComum:
                return Query([comum])
            if model is model_stream.Funcionario:
                return Query([funcionario])
            return Query([])

        def close(self):
            self.closed = True

    fake_db = FakeDb()
    monkeypatch.setattr(model_stream, "SessionLocal", lambda: fake_db)

    pessoas = model_stream.get_estatisticas()

    assert len(pessoas) == 3
    assert pessoas[0] == {
        "id": 1,
        "nome": "Procurado",
        "cpf": "111",
        "status": "Procurado",
        "isFuncionario": False,
        "foto": "foto-p",
    }
    assert pessoas[1] == {
        "id": 2,
        "nome": "Monitorado",
        "cpf": "222",
        "status": "Monitorado",
        "isFuncionario": False,
        "foto": "foto-c",
    }
    assert pessoas[2]["id"] == 3
    assert pessoas[2]["nome"] == "Funcionario"
    assert pessoas[2]["cpf"] == "333"
    assert pessoas[2]["isFuncionario"] is True
    assert pessoas[2]["foto"] is None
    assert fake_db.closed
