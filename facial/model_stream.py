import base64
import sys
from pathlib import Path
from typing import Optional

import cv2
import face_recognition
import numpy as np
from pydantic import BaseModel

from database.database import SessionLocal
from database.models import Funcionario, PessoaComum, Procurado
from facial.access_database import verify_face

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))


class PessoaPayload(BaseModel):
    nome: str
    cpf: str
    status: str
    isFuncionario: bool
    foto: Optional[str] = None


def decode_image(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


def is_face_inside_ellipse(top, right, bottom, left, center, axes):
    cx, cy = center
    a, b = axes
    corners = [(left, top), (right, top), (left, bottom), (right, bottom)]

    for x, y in corners:
        if ((x - cx) ** 2 / a**2) + ((y - cy) ** 2 / b**2) > 1:
            return False
    return True


def get_estatisticas():
    db = SessionLocal()
    try:
        procurados = db.query(Procurado).all()
        comuns = db.query(PessoaComum).all()
        funcs = db.query(Funcionario).all()

        pessoas = []
        for p in procurados:
            pessoas.append(
                {
                    "id": p.id,
                    "nome": p.nome,
                    "cpf": p.cpf,
                    "status": "Procurado",
                    "isFuncionario": False,
                    "foto": p.foto_base64,
                }
            )
        for c in comuns:
            pessoas.append(
                {
                    "id": c.id,
                    "nome": c.nome,
                    "cpf": c.cpf,
                    "status": "Monitorado",
                    "isFuncionario": False,
                    "foto": c.foto_base64,
                }
            )
        for f in funcs:
            pessoas.append(
                {
                    "id": f.id,
                    "nome": f.nome,
                    "cpf": f.cpf,
                    "status": "Funcionário",
                    "isFuncionario": True,
                    "foto": None,
                }
            )

        return pessoas
    finally:
        db.close()


def analisar_foto_streamlit(bytes_foto):

    # Converte os bytes puros do Streamlit para um array NumPy
    nparr = np.frombuffer(bytes_foto, np.uint8)

    # Decodifica o array em uma imagem (matriz BGR) do OpenCV
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return []

    # Reduz a imagem para 25% do tamanho original
    # Isso impede que o Streamlit feche a conexão por falta de memória ou timeout
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Converte BGR (OpenCV) para RGB padrão do face_recognition usando a imagem menor
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Encontra onde estão os rostos na imagem
    face_locations = face_recognition.face_locations(rgb_small_frame)
    responses = []

    for top, right, bottom, left in face_locations:
        # Pega as características do rosto encontrado
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, [(top, right, bottom, left)]
        )

        if not face_encodings:
            continue

        face_encoding = face_encodings[0]
        encoding_list = face_encoding.tolist()

        db_result = verify_face(encoding_list)

        responses.append(db_result)

    return responses
