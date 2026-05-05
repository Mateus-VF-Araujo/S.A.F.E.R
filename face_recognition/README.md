# Facial Recognition Module

Este módulo é responsável por processar uma stream de vídeo recebida via WebSocket, isolar rostos com base em uma Região de Interesse (ROI) elíptica, gerar o encoding biométrico e verificar o status do indivíduo no banco de dados.

## Bibliotecas Utilizadas

*   **IMPORTANTE:** o arquivo `dlib-19.22.99-cp310-cp310-win_amd64.whl` deve ser instalado manualmente antes de tudo, caso algum de vocês esteja usando Windows -> Execute `uv pip install face_recognition\utils\dlib-19.22.99-cp310-cp310-win_amd64.whl` na pasta raiz do projeto antes de sincronizar os pacotes com `uv pip install...`


*   **`fastapi`**, **`uvicorn`**, **`websockets`**: Servidor web e stream de vídeo bidirecional.
*   **`sqlalchemy`**: Usado para manipulação do banco de dados SQLite.
*   **`opencv-python`**: Visão computacional e decodificação Base64.
*   **`face_recognition`**: Detecção de rosto e extração de características.
*   **`numpy<2`**: Manipulação de arrays (versão estritamente < 2.0 para compatibilidade com o dlib).

## Comunicação com o React (Stream de Vídeo)

O módulo opera escutando conexões ativas de WebSocket no endpoint `/ws/recognition`. O React deve enviar pacotes contínuos (recomendado a no máximo 10 FPS).

### Payload de recepção (Dados esperados pelo módulo)
```json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "ellipse_center": [320, 240],
  "ellipse_axes": [150, 200]
}
```

### Payload de resposta (Dados retornados pelo módulo)

**Caso 1: Pessoa Procurada (Alerta)**
```json
{
  "results": [
    {
      "status": "wanted_alert",
      "cpf": "12345678900",
      "full_name": "Joãozin da Silva",
      "crime": "Roubo qualificado",
      "risk_level": "ALTO"
    }
  ]
}
```

**Caso 2: Pessoa Comum (Liberada)**
```json
{
  "results": [
    {
      "status": "common_cleared",
      "cpf": "45678912300",
      "full_name": "Mariazinha Souza"
    }
  ]
}
```

**Caso 3: Pessoa Funcionária (Tem acesso ao sistema)**
```json
{
  "results": [
    {
      "status": "employee_authorized",
      "cpf": "98765432100",
      "full_name": "Carlos Administrador"
    }
  ]
}
```

**Caso 4: Desconhecido**
```json
{
  "results": [
    {
      "status": "unknown"
    }
  ]
}
```