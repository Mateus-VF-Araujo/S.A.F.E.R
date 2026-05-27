from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Antes de rodar esse script, é necessário que o MySQL esteja rodando e que o banco safer_db exista. 
# Pode ser criado usando um cliente MySQL ou via linha de comando com:
# mysql -u 'usuario' -p -e "CREATE DATABASE safer_db;"

# Substitua usuario, senha, host, porta e nome do banco pelos dados locais
DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/safer_db"

# Cria o motor de conexao
engine = create_engine(DATABASE_URL, echo=True)

# Cria uma fabrica de sessoes para interagir com o BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Esse comando cria no MySQL as tabelas mapeadas pelas classes que herdam da Base
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    init_db()
