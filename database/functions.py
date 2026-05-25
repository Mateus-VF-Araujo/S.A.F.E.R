import base64
import numpy as np
import cv2

def decodificar_base64_para_cv2(string_base64: str):

    # 1. Remove o prefixo do Base64 caso o frontend envie (ex: "data:image/jpeg;base64,...")
    if "," in string_base64:
        string_base64 = string_base64.split(",")[1]
        
    # 2. Decodifica a string para bytes
    img_bytes = base64.b64decode(string_base64)
    
    # 3. Converte os bytes para um array unidimensional do NumPy
    np_array = np.frombuffer(img_bytes, dtype=np.uint8)
    
    # 4. Decodifica o array no formato de imagem do OpenCV (BGR)
    imagem_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    return imagem_cv2