import base64
from pathlib import Path
import numpy as np
import cv2

try:
    from models import Funcionario, PessoaComum, Procurado
except ModuleNotFoundError:
    from database.models import Funcionario, PessoaComum, Procurado


def remover_prefixo_base64(string_base64: str) -> str:
    # Alguns clientes enviam a imagem como data URL; o banco guarda apenas o Base64 puro.
    if "," in string_base64:
        return string_base64.split(",", 1)[1]

    return string_base64


def codificar_imagem_para_base64(caminho_imagem) -> str:
    # Le a imagem do disco e transforma seus bytes em uma string Base64.
    caminho_imagem = Path(caminho_imagem)
    return base64.b64encode(caminho_imagem.read_bytes()).decode("utf-8")

def decodificar_imagem_base64(string_base64: str):

    # Remove o prefixo do Base64 caso o frontend envie (ex: "data:image/jpeg;base64,...")
    string_base64 = remover_prefixo_base64(string_base64)
        
    # Decodifica a string para bytes
    img_bytes = base64.b64decode(string_base64)
    
    # Converte os bytes para um array unidimensional do NumPy
    np_array = np.frombuffer(img_bytes, dtype=np.uint8)
    
    # Decodifica o array no formato de imagem do OpenCV (BGR)
    imagem_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    return imagem_cv2

def validar_foto_base64(foto_base64: str) -> str:
    # Garante que a string recebida realmente pode ser aberta como imagem pelo OpenCV.
    foto_base64 = remover_prefixo_base64(foto_base64)
    imagem = decodificar_imagem_base64(foto_base64)
    if imagem is None:
        raise ValueError("A foto em base64 nao pode ser decodificada como imagem.")

    return foto_base64


def validar_campos_modelo(model, dados):
    # Evita enviar campos inexistentes para o SQLAlchemy ao criar os registros.
    colunas_modelo = set(model.__table__.columns.keys())
    campos_invalidos = set(dados.keys()) - colunas_modelo

    if campos_invalidos:
        raise ValueError(
            f"Campos invalidos para {model.__name__}: {', '.join(sorted(campos_invalidos))}"
        )


def validar_campos_obrigatorios(dados, campos_obrigatorios):
    # Confere se os campos essenciais foram informados antes de persistir no banco.
    campos_faltando = [
        campo
        for campo in campos_obrigatorios
        if campo not in dados or dados[campo] in (None, "")
    ]

    if campos_faltando:
        raise ValueError(
            f"Campos obrigatorios ausentes: {', '.join(sorted(campos_faltando))}"
        )


def salvar_no_banco(session, instancia):
    # Centraliza o fluxo padrao de adicionar, confirmar e atualizar a instancia.
    session.add(instancia)
    session.commit()
    session.refresh(instancia)
    return instancia


def criar_funcionario(session, dados):
    # Funcionario precisa estar coerente com o modelo e ter credenciais basicas.
    validar_campos_modelo(Funcionario, dados)
    validar_campos_obrigatorios(
        dados,
        ["nome", "cargo", "nivel_acesso", "email", "senha_hash"],
    )

    funcionario = Funcionario(**dados)
    return salvar_no_banco(session, funcionario)


def criar_procurado(session, dados, cadastrador_id):
    # O procurado sempre fica vinculado ao funcionario que realizou o cadastro.
    dados_procurado = {**dados, "cadastrado_por": cadastrador_id}

    validar_campos_modelo(Procurado, dados_procurado)
    validar_campos_obrigatorios(dados_procurado, ["nome", "foto_base64"])
    dados_procurado["foto_base64"] = validar_foto_base64(
        dados_procurado["foto_base64"]
    )

    procurado = Procurado(**dados_procurado)
    return salvar_no_banco(session, procurado)


def criar_pessoa_comum(session, dados, cadastrador_id):
    # A pessoa comum sempre fica vinculada ao funcionario que realizou o cadastro.
    dados_pessoa = {**dados, "cadastrado_por": cadastrador_id}

    validar_campos_modelo(PessoaComum, dados_pessoa)
    validar_campos_obrigatorios(dados_pessoa, ["nome", "foto_base64"])
    dados_pessoa["foto_base64"] = validar_foto_base64(dados_pessoa["foto_base64"])

    pessoa = PessoaComum(**dados_pessoa)
    return salvar_no_banco(session, pessoa)