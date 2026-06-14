import sys
from pathlib import Path

import cv2
import face_recognition
import numpy as np
import streamlit as st

from database.database import SessionLocal
from database.functions import decodificar_imagem_base64
from database.models import PessoaComum, Procurado

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))


@st.cache_resource
def carregar_banco_biometrico():
    encodings = []
    metadata = []
    db = SessionLocal()

    try:
        print("\n Iniciando carregamento do banco de dados")

        procurados = db.query(Procurado).all()
        for p in procurados:
            if p.foto_base64:
                # Se o texto da foto for maior que ~800KB, pula antes de quebrar
                if len(p.foto_base64) > 800000:
                    print(
                        f"Foto do Procurado ID {p.id} ({p.nome}) ignorada (Tamanho excessivo: {len(p.foto_base64)} caracteres)."
                    )
                    continue

                try:
                    print(f"Processando Procurado ID: {p.id} - Nome: {p.nome}")
                    imagem_cv2 = decodificar_imagem_base64(p.foto_base64)

                    if imagem_cv2 is not None:
                        altura, largura = imagem_cv2.shape[:2]
                        if largura > 800 or altura > 800:
                            fator = 800.0 / max(largura, altura)
                            imagem_cv2 = cv2.resize(
                                imagem_cv2, (int(largura * fator), int(altura * fator))
                            )

                        # Remove canal de transparência se a imagem for RGBA (PNG)
                        if imagem_cv2.shape[2] == 4:
                            imagem_cv2 = cv2.cvtColor(imagem_cv2, cv2.COLOR_BGRA2BGR)

                        # Converte para RGB criando um bloco de memória novo
                        rgb_frame = cv2.cvtColor(imagem_cv2, cv2.COLOR_BGR2RGB)

                        rgb_frame_seguro = np.ascontiguousarray(rgb_frame)

                        face_encs = face_recognition.face_encodings(rgb_frame_seguro)

                        if face_encs:
                            encodings.append(face_encs[0])
                            metadata.append(
                                {
                                    "status": "wanted_alert",
                                    "cpf": p.cpf,
                                    "full_name": p.nome,
                                    "crime": "Não especificado",
                                    "risk_level": str(p.nivel_periculosidade),
                                }
                            )
                    else:
                        print(
                            f"Foto não pôde ser decodificada para o Procurado ID: {p.id}"
                        )

                except Exception as e:
                    print(f"Pulando foto corrompida do Procurado ID {p.id}. Erro: {e}")
                    continue

        print("\nCarregando Pessoas Comuns")
        pessoas_comuns = db.query(PessoaComum).all()
        for p in pessoas_comuns:
            if p.foto_base64:
                if len(p.foto_base64) > 800000:
                    print(
                        f"Foto da Pessoa Comum ID {p.id} ({p.nome}) ignorada (Tamanho excessivo: {len(p.foto_base64)} caracteres)."
                    )
                    continue

                try:
                    print(f"Processando Pessoa Comum ID: {p.id} - Nome: {p.nome}")
                    imagem_cv2 = decodificar_imagem_base64(p.foto_base64)

                    if imagem_cv2 is not None:
                        altura, largura = imagem_cv2.shape[:2]
                        if largura > 800 or altura > 800:
                            fator = 800.0 / max(largura, altura)
                            imagem_cv2 = cv2.resize(
                                imagem_cv2, (int(largura * fator), int(altura * fator))
                            )

                        # Remove canal de transparência se a imagem for RGBA (PNG)
                        if imagem_cv2.shape[2] == 4:
                            imagem_cv2 = cv2.cvtColor(imagem_cv2, cv2.COLOR_BGRA2BGR)

                        # Converte para RGB criando um bloco de memória novo
                        rgb_frame = cv2.cvtColor(imagem_cv2, cv2.COLOR_BGR2RGB)

                        rgb_frame_seguro = np.ascontiguousarray(rgb_frame)

                        face_encs = face_recognition.face_encodings(rgb_frame_seguro)

                        if face_encs:
                            encodings.append(face_encs[0])
                            metadata.append(
                                {
                                    "status": "common_cleared",
                                    "cpf": p.cpf,
                                    "full_name": p.nome,
                                }
                            )
                    else:
                        print(
                            f"Foto não pôde ser decodificada para a Pessoa Comum ID: {p.id}"
                        )

                except Exception as e:
                    print(
                        f"Pulando foto corrompida da Pessoa Comum ID {p.id}. Erro: {e}"
                    )
                    continue

    except Exception as e_geral:
        print(f"Falha ao acessar o banco de dados: {e_geral}")
    finally:
        db.close()

    print(f"\n Cache Biométrico Finalizado {len(encodings)} faces carregadas na RAM.")
    return encodings, metadata


def verify_face(face_encoding_list):
    known_encodings, known_metadata = carregar_banco_biometrico()

    if not known_encodings:
        return {"status": "unknown"}

    target_encoding = np.array(face_encoding_list)
    matches = face_recognition.compare_faces(
        known_encodings,
        target_encoding,
        tolerance=0.7,
    )

    face_distances = face_recognition.face_distance(known_encodings, target_encoding)

    best_match_index = np.argmin(face_distances)
    melhor_distancia = face_distances[best_match_index]
    pessoa_encontrada = known_metadata[best_match_index]

    print(f"Câmera identificou como: {pessoa_encontrada['full_name']}")
    print(f"Tabela de origem: {pessoa_encontrada['status']}")
    print(f"Distância matemática: {melhor_distancia:.3f}")
    print("----------------------\n")

    if matches[best_match_index]:
        return pessoa_encontrada

    return {"status": "unknown"}
