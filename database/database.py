from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Substitua usuario, senha, host, porta e nome do banco pelos dados locais
DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/safer_db"

# Cria o motor de conexao
engine = create_engine(DATABASE_URL, echo=True)

# Cria uma fabrica de sessoes para interagir com o BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Esse comando cria no MySQL as tabelas mapeadas pelas classes que herdam da Base
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas")


if __name__ == "__main__":
    init_db()