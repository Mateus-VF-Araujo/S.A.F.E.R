import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Float, Date, String
import os

# Substitua usuario, senha, host, porta e nome do banco pelos dados locais
DATABASE_URL = "mysql+pymysql://root:root@localhost/safer_db"

engine = create_engine(DATABASE_URL, echo=False)

caminho_do_arquivo = r"C:\dev\S.A.F.E.R\database\BancoVDE2025.csv"

print("Inicio")
df = pd.read_csv(caminho_do_arquivo, sep=';', low_memory=False, decimal=',')

df_rn = df[df['uf'] == 'RN'].copy()

colunas_numericas = ['total_vitima', 'total', 'total_peso', 'feminino', 'masculino', 'nao_informado']
for coluna in colunas_numericas:
    if coluna in df_rn.columns:

        df_rn[coluna] = df_rn[coluna].fillna(0)
        
        if coluna == 'total_peso':
            df_rn[coluna] = df_rn[coluna].astype(float)
        else:
            df_rn[coluna] = df_rn[coluna].astype(int)

colunas_texto = ['municipio', 'arma', 'evento', 'agente', 'faixa_etaria']
for coluna in colunas_texto:
    if coluna in df_rn.columns:
        df_rn[coluna] = df_rn[coluna].fillna('NÃO INFORMADO')

if 'data_referencia' in df_rn.columns:
    df_rn['data_referencia'] = pd.to_datetime(df_rn['data_referencia'], dayfirst=True, errors='coerce')
    
    df_rn['data_referencia'] = df_rn['data_referencia'].dt.strftime('%Y-%m-%d')

print("Enviando para o banco de dados")

tipagem_banco = {
    'total_vitima': Integer(),
    'feminino': Integer(),
    'masculino': Integer(),
    'nao_informado': Integer(),
    'total': Integer(),
    'total_peso': Float(),
    'data_referencia': Date(), 
    'municipio': String(150),
    'arma': String(100),
    'evento': String(100),
    'agente': String(100),
    'faixa_etaria': String(50),
    'abrangencia': String(50),
    'uf': String(2)
}

df_rn.to_sql(
    name='dados_seguranca_publica', 
    con=engine, 
    if_exists='replace', 
    index=False,
    dtype=tipagem_banco
)

print(f"Fim")