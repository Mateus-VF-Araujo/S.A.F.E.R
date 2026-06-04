import sys
import json
import base64
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import face_recognition
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from database.database import SessionLocal
from database.models import Procurado, PessoaComum, Funcionario
from database.functions import criar_procurado, criar_pessoa_comum

from access_database import verify_face, load_encodings_to_memory

app = FastAPI(title="S.A.F.E.R. Biometric Stream API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PessoaPayload(BaseModel):
    nome: str
    cpf: str
    status: str
    isFuncionario: bool
    foto: Optional[str] = None

def decode_image(base64_string):
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def is_face_inside_ellipse(top, right, bottom, left, center, axes):
    cx, cy = center
    a, b = axes
    corners = [(left, top), (right, top), (left, bottom), (right, bottom)]
    
    for x, y in corners:
        if ((x - cx)**2 / a**2) + ((y - cy)**2 / b**2) > 1:
            return False
    return True

@app.post("/api/cadastrar_pessoa")
def api_cadastrar_pessoa(payload: PessoaPayload):
    db = SessionLocal()
    try:
        cadastrador_id = 1 
        
        if payload.status == "Procurado":
            dados = {
                "nome": payload.nome,
                "cpf": payload.cpf,
                "nivel_periculosidade": 3,
                "foto_base64": payload.foto
            }
            criar_procurado(db, dados, cadastrador_id)
            
        elif payload.status in ["Monitorado", "Suspeito"]:
            dados = {
                "nome": payload.nome,
                "cpf": payload.cpf,
                "foto_base64": payload.foto
            }
            criar_pessoa_comum(db, dados, cadastrador_id)
            
        load_encodings_to_memory()
        
        return {"ok": True, "message": "Pessoa gravada no banco MySQL e cache da IA sincronizado!"}
    except Exception as e:
        db.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        db.close()

@app.get("/api/estatisticas")
def api_get_estatisticas():
    db = SessionLocal()
    try:
        procurados = db.query(Procurado).all()
        comuns = db.query(PessoaComum).all()
        funcs = db.query(Funcionario).all()
        
        pessoas = []
        for p in procurados:
            pessoas.append({
                "id": p.id, 
                "nome": p.nome, 
                "cpf": p.cpf, 
                "status": "Procurado", 
                "isFuncionario": False, 
                "foto": p.foto_base64
            })
        for c in comuns:
            pessoas.append({
                "id": c.id, 
                "nome": c.nome, 
                "cpf": c.cpf, 
                "status": "Monitorado", 
                "isFuncionario": False, 
                "foto": c.foto_base64
            })
        for f in funcs:
            pessoas.append({
                "id": f.id, 
                "nome": f.nome, 
                "cpf": f.cpf, 
                "status": "Funcionário", 
                "isFuncionario": True, 
                "foto": None
            })
            
        return pessoas
    finally:
        db.close()

@app.websocket("/ws/recognition")
async def recognition_websocket(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Cliente conectado para análise de fluxo de vídeo.")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            frame_b64 = payload.get("frame")
            ellipse_center = payload.get("ellipse_center", (320, 240))
            ellipse_axes = payload.get("ellipse_axes", (150, 200))
            
            if not frame_b64:
                continue
                
            frame = decode_image(frame_b64)
            if frame is None:
                continue
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            responses = []
            
            for (top, right, bottom, left) in face_locations:
                if not is_face_inside_ellipse(top, right, bottom, left, ellipse_center, ellipse_axes):
                    continue 
                
                face_encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
                if not face_encodings:
                    continue
                    
                face_encoding = face_encodings[0]
                encoding_list = face_encoding.tolist()
                
                db_result = verify_face(encoding_list)
                responses.append(db_result)
            
            if responses:
                await websocket.send_json({"results": responses})
                
    except WebSocketDisconnect:
        print("[WebSocket] Cliente desconectou da stream.")
    except Exception as e:
        print(f"[WebSocket] Erro inesperado no fluxo do stream: {e}")
