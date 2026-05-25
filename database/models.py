from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(50), nullable=False)
    cpf = Column(String(14), unique=True)
    nivel_acesso = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)

    cadastros_realizados = relationship("Procurado", back_populates="cadastrado_por_func")

class Procurado(Base):
    __tablename__ = 'procurados'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True)
    nivel_periculosidade = Column(Integer)
    foto_base64 = Column(LONGTEXT, nullable=False) 
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    cadastrado_por = Column(Integer, ForeignKey('funcionarios.id'))

    cadastrado_por_func = relationship("Funcionario", back_populates="cadastros_realizados")

class PessoaComum(Base):
    __tablename__ = 'pessoa_comum'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True)
    foto_base64 = Column(LONGTEXT, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)