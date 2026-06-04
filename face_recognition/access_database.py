import numpy as np
import face_recognition
from database import SessionLocal
from models import Procurado, PessoaComum, Funcionario
from functions import decodificar_imagem_base64

known_encodings = []
known_metadata = []

def load_encodings_to_memory():
    """
    Carrega as fotos do banco MySQL, calcula os encodings e armazena na memória RAM
    para não atrasar o processamento do vídeo em tempo real.
    """
    global known_encodings, known_metadata
    known_encodings.clear()
    known_metadata.clear()
    
    db = SessionLocal()
    try:
        procurados = db.query(Procurado).all()
        for p in procurados:
            if p.foto_base64:
                imagem_cv2 = decodificar_imagem_base64(p.foto_base64)
                if imagem_cv2 is not None:
                    rgb_frame = imagem_cv2[:, :, ::-1]
                    encodings = face_recognition.face_encodings(rgb_frame)
                    if encodings:
                        known_encodings.append(encodings[0])
                        known_metadata.append({
                            "status": "wanted_alert",
                            "cpf": p.cpf,
                            "full_name": p.nome,
                            "crime": "Não especificado",
                            "risk_level": str(p.nivel_periculosidade)
                        })

        pessoas_comuns = db.query(PessoaComum).all()
        for p in pessoas_comuns:
            if p.foto_base64:
                imagem_cv2 = decodificar_imagem_base64(p.foto_base64)
                if imagem_cv2 is not None:
                    rgb_frame = imagem_cv2[:, :, ::-1]
                    encodings = face_recognition.face_encodings(rgb_frame)
                    if encodings:
                        known_encodings.append(encodings[0])
                        known_metadata.append({
                            "status": "common_cleared",
                            "cpf": p.cpf,
                            "full_name": p.nome
                        })  
    finally:
        db.close()
        
    print(f"[Cache Biométrico] {len(known_encodings)} faces carregadas na memória com sucesso.")

load_encodings_to_memory()

def verify_face(face_encoding_list):
    """
    Compara o encoding recebido do stream com os encodings armazenados em cache.
    """
    if not known_encodings:
        return {"status": "unknown"}
        
    target_encoding = np.array(face_encoding_list)
    matches = face_recognition.compare_faces(known_encodings, target_encoding, tolerance=0.6)
    face_distances = face_recognition.face_distance(known_encodings, target_encoding)
    
    best_match_index = np.argmin(face_distances)
    
    if matches[best_match_index]:
        return known_metadata[best_match_index]
        
    return {"status": "unknown"}
