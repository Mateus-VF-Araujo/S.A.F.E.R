from pathlib import Path

from sqlalchemy.exc import IntegrityError
from database import SessionLocal, init_db
from functions import (
    codificar_imagem_para_base64,
    validar_campos_modelo,
    validar_foto_base64,
)
from models import Funcionario, PessoaComum, Procurado


PASTA_FOTOS_PROCURADOS = Path(__file__).resolve().parent / "fotosProcurados"
CADASTRADOR_PROCURADOS_EMAIL = "mariasilva@safer.local"
CADASTRADOR_PESSOAS_COMUNS_EMAIL = CADASTRADOR_PROCURADOS_EMAIL


def carregar_foto_base64(nome_arquivo: str) -> str:
    # Carrega as fotos de exemplo da pasta local e salva o conteudo em Base64.
    caminho_foto = PASTA_FOTOS_PROCURADOS / nome_arquivo
    return codificar_imagem_para_base64(caminho_foto)


# Imagem minima usada como foto valida para registros de exemplo sem arquivo proprio.
FOTO_EXEMPLO_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwAD"
    "hgGAWjR9awAAAABJRU5ErkJggg=="
)


# Dados iniciais de funcionarios que podem acessar o sistema.
FUNCIONARIOS = [
    {
        "nome": "João Machado",
        "cargo": "Administrador",
        "cpf": "000.000.000-00",
        "nivel_acesso": 3,
        "email": "joaomachado@safer.local",
        "senha_hash": "joaomachado123",
        "ativo": True,
    },
    {
        "nome": "Maria Silva",
        "cargo": "Analista de Segurança",
        "cpf": "111.111.111-11",
        "nivel_acesso": 2,
        "email": "mariasilva@safer.local",
        "senha_hash": "mariasilva123",
        "ativo": True,
    },
]


# Registros iniciais de procurados usados para demonstracao e testes locais.
PROCURADOS = [
    {
        "nome": "Kennymar Bezerra de Oliveira",
        "cpf": "222.222.222-22",
        "nivel_periculosidade": 4,
        "foto_base64": carregar_foto_base64("kenymar.jpeg"),
    },
    {
        "nome": "Guilherme Souza de Farias",
        "cpf": "333.333.333-33",
        "nivel_periculosidade": 3,
        "foto_base64": carregar_foto_base64("guilherme.jpeg"),
    },
    {
        "nome": "Soraia Pereira de Araújo",
        "cpf": "444.444.444-44",
        "nivel_periculosidade": 2,
        "foto_base64": carregar_foto_base64("soraia.jpeg"),
    },
    {
        "nome": "Mateus Vinicius Figueredo de Araújo",
        "cpf": "555.555.555-55",
        "nivel_periculosidade": 1,
        "foto_base64": carregar_foto_base64("mateus.jpeg"),
    },
]


# Registros comuns usados para validar fluxos que nao envolvem pessoas procuradas.
PESSOAS_COMUNS = [
    {
        "nome": "Carlos Pereira",
        "cpf": "666.666.666-66",
        "foto_base64": FOTO_EXEMPLO_BASE64,
    }
]


def get_or_create(session, model, defaults=None, **filtros):
    # Procura pelo registro usando os filtros; se nao existir, cria sem duplicar dados.
    instancia = session.query(model).filter_by(**filtros).first()
    if instancia:
        return instancia, False

    dados = {**filtros, **(defaults or {})}
    instancia = model(**dados)
    session.add(instancia)
    return instancia, True


def popular_funcionarios(session):
    # Guarda os funcionarios por email para recuperar depois quem cadastrara os procurados.
    funcionarios_por_email = {}

    for dados in FUNCIONARIOS:
        # Valida os campos antes de tentar criar cada linha no banco.
        validar_campos_modelo(Funcionario, dados)
        email = dados["email"]
        funcionario, criado = get_or_create(
            session,
            Funcionario,
            defaults={chave: valor for chave, valor in dados.items() if chave != "email"},
            email=email,
        )
        funcionarios_por_email[email] = funcionario
        print(f"{'Criado' if criado else 'Ja existe'} funcionario: {funcionario.email}")

    session.flush()
    return funcionarios_por_email


def popular_procurados(session, cadastrador_id):
    for dados in PROCURADOS:
        # A foto e validada antes da criacao para evitar registros com Base64 quebrado.
        validar_campos_modelo(Procurado, dados)
        foto_base64 = validar_foto_base64(dados["foto_base64"])

        procurado, criado = get_or_create(
            session,
            Procurado,
            defaults={
                "nome": dados["nome"],
                "nivel_periculosidade": dados["nivel_periculosidade"],
                "foto_base64": foto_base64,
                "cadastrado_por": cadastrador_id,
            },
            cpf=dados["cpf"],
        )
        print(f"{'Criado' if criado else 'Ja existe'} procurado: {procurado.cpf}")


def popular_pessoas_comuns(session, cadastrador_id):
    for dados in PESSOAS_COMUNS:
        # A pessoa comum tambem fica vinculada ao funcionario que realizou o cadastro.
        dados_pessoa = {**dados, "cadastrado_por": cadastrador_id}

        validar_campos_modelo(PessoaComum, dados_pessoa)
        foto_base64 = validar_foto_base64(dados_pessoa["foto_base64"])

        pessoa, criado = get_or_create(
            session,
            PessoaComum,
            defaults={
                "nome": dados_pessoa["nome"],
                "foto_base64": foto_base64,
                "cadastrado_por": cadastrador_id,
            },
            cpf=dados_pessoa["cpf"],
        )
        if not criado and pessoa.cadastrado_por != cadastrador_id:
            pessoa.cadastrado_por = cadastrador_id

        print(f"{'Criada' if criado else 'Ja existe'} pessoa comum: {pessoa.cpf}")


def popular_banco():
    # Inicializa as tabelas e popula tudo em uma unica transacao.
    init_db()
    session = SessionLocal()

    try:
        funcionarios_por_email = popular_funcionarios(session)
        cadastrador_procurados = funcionarios_por_email[CADASTRADOR_PROCURADOS_EMAIL]
        cadastrador_pessoas_comuns = funcionarios_por_email[CADASTRADOR_PESSOAS_COMUNS_EMAIL]
        popular_procurados(session, cadastrador_procurados.id)
        popular_pessoas_comuns(session, cadastrador_pessoas_comuns.id)
        session.commit()
        print("Banco populado com sucesso.")
    except (IntegrityError, ValueError) as erro:
        session.rollback()
        print(f"Erro ao popular banco: {erro}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    popular_banco()