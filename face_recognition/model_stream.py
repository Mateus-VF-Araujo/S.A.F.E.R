import cv2
import numpy as np
import base64
import json
import face_recognition
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from access_database import verify_face

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def decode_image(base64_string):
    img_data = base64.b64decode(base64_string.split(',')[1] if ',' in base64_string else base64_string)
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

@app.websocket("/ws/recognition")
async def recognition_websocket(websocket: WebSocket):
    await websocket.accept()
    
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
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            responses = []
            
            for (top, right, bottom, left) in face_locations:
                if not is_face_inside_ellipse(top, right, bottom, left, ellipse_center, ellipse_axes):
                    continue 
                
                face_encoding = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])[0]
                encoding_list = face_encoding.tolist()
                
                db_result = verify_face(encoding_list)
                responses.append(db_result)
            
            if responses:
                await websocket.send_json({"results": responses})
                
    except WebSocketDisconnect:
        pass
    