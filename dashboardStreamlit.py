import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.models import Funcionario, PessoaComum, Procurado


st.set_page_config(page_title="S.A.F.E.R. - Dashboard", layout="wide")

DATABASE_URL = os.getenv(
    "SAFER_DATABASE_URL",
    "mysql+pymysql://root:root@localhost:3306/safer_db",
)

FOTO_EXEMPLO_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwAD"
    "hgGAWjR9awAAAABJRU5ErkJggg=="
)


@st.cache_resource
def get_db_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def executar_sql(query, params=None):
    with engine.begin() as conn:
        return conn.execute(text(query), params or {})

def registrar_mensagem_crud(mensagem):
    st.session_state["crud_mensagem"] = mensagem

def exibir_mensagem_crud():
    mensagem = st.session_state.pop("crud_mensagem", None)
    if not mensagem:
        return

    if "sucesso" in mensagem:
        st.success(mensagem)
    else:
        st.error(mensagem)

def buscar_estatisticas_safer():
    with SessionLocal() as session:
        total_procurados = session.query(Procurado).count()
        total_funcionarios = session.query(Funcionario).count()
        total_comuns = session.query(PessoaComum).count()
        niveis_query = session.query(Procurado.nivel_periculosidade).all()

    df_niveis = pd.DataFrame(niveis_query, columns=["Nivel"])
    return total_procurados, total_funcionarios, total_comuns, df_niveis

def buscar_procurados(termo_busca):
    with SessionLocal() as session:
        resultados = (
            session.query(Procurado)
            .filter(
                (Procurado.nome.ilike(f"%{termo_busca}%"))
                | (Procurado.cpf.ilike(f"%{termo_busca}%"))
            )
            .all()
        )
        dados = [
            {
                "ID": p.id,
                "Foto": p.foto_base64[:30] + "..." if p.foto_base64 else "Sem foto",
                "Nome": p.nome,
                "CPF": p.cpf,
                "Nivel Periculosidade": p.nivel_periculosidade,
                "Data Cadastro": p.data_cadastro,
                "Cadastrado Por": p.cadastrado_por,
            }
            for p in resultados
        ]
        return pd.DataFrame(dados)

@st.cache_data(ttl=120)
def carregar_dados_publicos_db():
    query = "SELECT * FROM dados_seguranca_publica"
    return pd.read_sql(query, engine)

def preparar_dados_publicos(df):
    df = df.copy()
    colunas_numericas = [
        "feminino",
        "masculino",
        "nao_informado",
        "total_vitima",
        "total",
        "total_peso",
    ]
    for coluna in colunas_numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)

    if "data_referencia" in df.columns:
        df["data_referencia"] = pd.to_datetime(
            df["data_referencia"],
            dayfirst=True,
            errors="coerce",
        )
        df["mes_referencia"] = df["data_referencia"].dt.to_period("M").astype(str)

    for coluna in ["uf", "municipio", "evento", "agente", "arma", "faixa_etaria", "abrangencia"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("NAO INFORMADO").astype(str)

    return df

def aplicar_filtros_publicos(df):
    st.subheader("Filtros de Análise")
    col1, col2, col3, col4 = st.columns(4)
    df_filtrado = df.copy()

    with col1:
        if "uf" in df.columns:
            ufs = st.multiselect(
                "UF",
                sorted(df["uf"].dropna().unique()),
                default=sorted(df["uf"].dropna().unique())[:1],
            )
            if ufs:
                df_filtrado = df_filtrado[df_filtrado["uf"].isin(ufs)]

    with col2:
        if "municipio" in df.columns:
            municipios = st.multiselect(
                "Municípios",
                sorted(df_filtrado["municipio"].dropna().unique()),
                max_selections=10,
            )
            if municipios:
                df_filtrado = df_filtrado[df_filtrado["municipio"].isin(municipios)]

    with col3:
        if "evento" in df.columns:
            eventos = st.multiselect(
                "Eventos",
                sorted(df_filtrado["evento"].dropna().unique()),
                max_selections=8,
            )
            if eventos:
                df_filtrado = df_filtrado[df_filtrado["evento"].isin(eventos)]

    with col4:
        if "data_referencia" in df.columns and df["data_referencia"].notna().any():
            data_min = df["data_referencia"].min().date()
            data_max = df["data_referencia"].max().date()
            periodo = st.date_input(
                "Período",
                value=(data_min, data_max),
                min_value=data_min,
                max_value=data_max,
            )
            if len(periodo) == 2:
                inicio, fim = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
                df_filtrado = df_filtrado[
                    (df_filtrado["data_referencia"] >= inicio)
                    & (df_filtrado["data_referencia"] <= fim)
                ]

    return df_filtrado

def exibir_metricas_publicas(df):
    total_vitimas = int(df["total_vitima"].sum()) if "total_vitima" in df.columns else 0
    media_vitimas = df["total_vitima"].mean() if "total_vitima" in df.columns else 0
    max_vitimas = int(df["total_vitima"].max()) if "total_vitima" in df.columns else 0
    min_vitimas = int(df["total_vitima"].min()) if "total_vitima" in df.columns else 0
    municipios = df["municipio"].nunique() if "municipio" in df.columns else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("SUM vítimas", f"{total_vitimas:,}".replace(",", "."))
    col2.metric("AVG por registro", f"{media_vitimas:.2f}")
    col3.metric("MAX em registro", max_vitimas)
    col4.metric("MIN em registro", min_vitimas)
    col5.metric("Municípios", municipios)

def exibir_graficos_publicos(df):
    if "total_vitima" not in df.columns:
        st.warning("A coluna total_vitima nao foi encontrada.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Ranking",
            "Evolução Temporal",
            "Perfil das Vítimas",
            "Armas e Agentes",
            "Tabela Estatística",
        ]
    )

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if "municipio" in df.columns:
                top_municipios = (
                    df.groupby("municipio", as_index=False)["total_vitima"]
                    .sum()
                    .sort_values("total_vitima", ascending=False)
                    .head(12)
                )
                fig = px.bar(
                    top_municipios,
                    x="total_vitima",
                    y="municipio",
                    orientation="h",
                    title="Municípios com maior total de vítimas",
                    labels={"total_vitima": "Total de vítimas", "municipio": "Município "},
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "evento" in df.columns:
                top_eventos = (
                    df.groupby("evento", as_index=False)["total_vitima"]
                    .sum()
                    .sort_values("total_vitima", ascending=False)
                    .head(10)
                )
                fig = px.bar(
                    top_eventos,
                    x="total_vitima",
                    y="evento",
                    orientation="h",
                    title="Eventos com maior total de vitimas",
                    labels={"total_vitima": "Total de vitimas", "evento": "Evento"},
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

        if {"municipio", "evento"}.issubset(df.columns):
            base_mapa = (
                df.groupby(["municipio", "evento"], as_index=False)["total_vitima"]
                .sum()
                .sort_values("total_vitima", ascending=False)
                .head(80)
            )
            matriz = base_mapa.pivot_table(
                index="municipio",
                columns="evento",
                values="total_vitima",
                aggfunc="sum",
                fill_value=0,
            )
            fig = px.imshow(
                matriz,
                aspect="auto",
                title="Mapa de calor: municípios x eventos",
                labels={"color": "Vítimas"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if "mes_referencia" in df.columns:
            serie = (
                df.groupby("mes_referencia", as_index=False)["total_vitima"]
                .sum()
                .sort_values("mes_referencia")
            )
            fig = px.line(
                serie,
                x="mes_referencia",
                y="total_vitima",
                markers=True,
                title="Evolução mensal do total de vítimas",
                labels={"mes_referencia": "Mês", "total_vitima": "Total de vítimas"},
            )
            st.plotly_chart(fig, use_container_width=True)

            maior_mes = serie.loc[serie["total_vitima"].idxmax()]
            menor_mes = serie.loc[serie["total_vitima"].idxmin()]
            col1, col2 = st.columns(2)
            col1.info(f"Mes com maior total: {maior_mes['mes_referencia']} ({int(maior_mes['total_vitima'])})")
            col2.info(f"Mes com menor total: {menor_mes['mes_referencia']} ({int(menor_mes['total_vitima'])})")
        else:
            st.info("A coluna data_referencia nao esta disponivel para serie temporal.")

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            colunas_genero = [c for c in ["feminino", "masculino", "nao_informado"] if c in df.columns]
            if colunas_genero:
                genero = (
                    df[colunas_genero]
                    .sum()
                    .reset_index()
                    .rename(columns={"index": "grupo", 0: "total"})
                )
                fig = px.pie(
                    genero,
                    names="grupo",
                    values="total",
                    title="Distribuição por sexo informado",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "faixa_etaria" in df.columns:
                faixa = (
                    df.groupby("faixa_etaria", as_index=False)["total_vitima"]
                    .sum()
                    .sort_values("total_vitima", ascending=False)
                    .head(10)
                )
                fig = px.bar(
                    faixa,
                    x="faixa_etaria",
                    y="total_vitima",
                    title="Vítimas por faixa etária",
                    labels={"faixa_etaria": "Faixa etária", "total_vitima": "Vítimas"},
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            if "arma" in df.columns:
                armas = (
                    df.groupby("arma", as_index=False)["total_vitima"]
                    .sum()
                    .sort_values("total_vitima", ascending=False)
                    .head(10)
                )
                fig = px.bar(
                    armas,
                    x="total_vitima",
                    y="arma",
                    orientation="h",
                    title="Armas associadas ao maior total de vítimas",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "agente" in df.columns:
                agentes = (
                    df.groupby("agente", as_index=False)["total_vitima"]
                    .sum()
                    .sort_values("total_vitima", ascending=False)
                    .head(10)
                )
                fig = px.bar(
                    agentes,
                    x="total_vitima",
                    y="agente",
                    orientation="h",
                    title="Agentes com maior total registrado",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

    with tab5:
        dimensao = st.selectbox(
            "Agrupar estatísticas por",
            [c for c in ["municipio", "evento", "arma", "agente", "faixa_etaria", "uf"] if c in df.columns],
        )
        resumo = (
            df.groupby(dimensao)["total_vitima"]
            .agg(registros="count", SUM="sum", AVG="mean", MAX="max", MIN="min")
            .reset_index()
            .sort_values("SUM", ascending=False)
        )
        resumo["AVG"] = resumo["AVG"].round(2)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

def listar_funcionarios():
    with SessionLocal() as session:
        dados = [
            {
                "id": f.id,
                "nome": f.nome,
                "cargo": f.cargo,
                "cpf": f.cpf,
                "nivel_acesso": f.nivel_acesso,
                "email": f.email,
                "ativo": f.ativo,
            }
            for f in session.query(Funcionario).order_by(Funcionario.id).all()
        ]
    return pd.DataFrame(dados)

def listar_procurados():
    with SessionLocal() as session:
        dados = [
            {
                "id": p.id,
                "foto": p.foto_base64[:30] + "..." if p.foto_base64 else "Sem foto",
                "nome": p.nome,
                "cpf": p.cpf,
                "nivel_periculosidade": p.nivel_periculosidade,
                "data_cadastro": p.data_cadastro,
                "cadastrado_por": p.cadastrado_por,
            }
            for p in session.query(Procurado).order_by(Procurado.id).all()
        ]
    return pd.DataFrame(dados)

def listar_pessoas_comuns():
    with SessionLocal() as session:
        dados = [
            {
                "id": p.id,
                "foto": p.foto_base64[:30] + "..." if p.foto_base64 else "Sem foto",
                "nome": p.nome,
                "cpf": p.cpf,
                "data_cadastro": p.data_cadastro,
                "cadastrado_por": p.cadastrado_por,
            }
            for p in session.query(PessoaComum).order_by(PessoaComum.id).all()
        ]
    return pd.DataFrame(dados)

def opcoes_funcionarios():
    df = listar_funcionarios()
    if df.empty:
        return {}
    return {f"{row.nome} - ID {row.id}": int(row.id) for row in df.itertuples()}

def criar_registro(modelo, dados):
    with SessionLocal() as session:
        try:
            session.add(modelo(**dados))
            session.commit()
            return "Registro inserido com sucesso."
        except IntegrityError as erro:
            session.rollback()
            return f"Erro de integridade: {erro.orig}"
        except Exception as erro:
            session.rollback()
            return f"Erro ao inserir: {erro}"

def atualizar_registro(modelo, registro_id, dados):
    with SessionLocal() as session:
        registro = session.get(modelo, registro_id)
        if not registro:
            return "Registro nao encontrado."

        try:
            for campo, valor in dados.items():
                setattr(registro, campo, valor)
            session.commit()
            return "Registro atualizado com sucesso."
        except IntegrityError as erro:
            session.rollback()
            return f"Erro de integridade: {erro.orig}"
        except Exception as erro:
            session.rollback()
            return f"Erro ao atualizar: {erro}"

def remover_registro(modelo, registro_id):
    with SessionLocal() as session:
        registro = session.get(modelo, registro_id)
        if not registro:
            return "Registro nao encontrado."

        try:
            session.delete(registro)
            session.commit()
            return "Registro removido com sucesso."
        except Exception as erro:
            session.rollback()
            return f"Erro ao remover: {erro}"

def criar_view_resumo():
    query = """
    CREATE OR REPLACE VIEW vw_resumo_cadastros_safer AS
    SELECT
        f.id AS funcionario_id,
        f.nome AS funcionario,
        f.cargo,
        COUNT(DISTINCT p.id) AS total_procurados_cadastrados,
        COUNT(DISTINCT pc.id) AS total_pessoas_comuns_cadastradas,
        MAX(p.nivel_periculosidade) AS maior_nivel_periculosidade_cadastrado
    FROM funcionarios f
    LEFT JOIN procurados p ON p.cadastrado_por = f.id
    LEFT JOIN pessoa_comum pc ON pc.cadastrado_por = f.id
    GROUP BY f.id, f.nome, f.cargo
    """
    executar_sql(query)

def exibir_crud_funcionarios():
    st.subheader("Funcionarios")
    exibir_mensagem_crud()
    df = listar_funcionarios()
    st.dataframe(df, use_container_width=True, hide_index=True)

    criar, editar, remover = st.tabs(["Inserir", "Alterar", "Remover"])
    with criar:
        with st.form("criar_funcionario"):
            nome = st.text_input("Nome")
            cargo = st.text_input("Cargo", value="Analista de Seguranca")
            cpf = st.text_input("CPF")
            nivel = st.number_input("Nivel de acesso", min_value=1, max_value=5, value=2)
            email = st.text_input("Email")
            senha = st.text_input("Senha/Hash", type="password")
            ativo = st.checkbox("Ativo", value=True)
            if st.form_submit_button("Inserir funcionario"):
                msg = criar_registro(
                    Funcionario,
                    {
                        "nome": nome,
                        "cargo": cargo,
                        "cpf": cpf,
                        "nivel_acesso": int(nivel),
                        "email": email,
                        "senha_hash": senha,
                        "ativo": ativo,
                    },
                )
                registrar_mensagem_crud(msg)
                st.rerun()

    with editar:
        if not df.empty:
            registro_id = st.selectbox("Funcionario para alterar", df["id"].tolist())
            atual = df[df["id"] == registro_id].iloc[0]
            with st.form("editar_funcionario"):
                nome = st.text_input("Nome", value=atual["nome"])
                cargo = st.text_input("Cargo", value=atual["cargo"])
                cpf = st.text_input("CPF", value=atual["cpf"])
                nivel = st.number_input(
                    "Nivel de acesso",
                    min_value=1,
                    max_value=5,
                    value=int(atual["nivel_acesso"]),
                )
                email = st.text_input("Email", value=atual["email"])
                ativo = st.checkbox("Ativo", value=bool(atual["ativo"]))
                if st.form_submit_button("Salvar alteracoes"):
                    msg = atualizar_registro(
                        Funcionario,
                        int(registro_id),
                        {
                            "nome": nome,
                            "cargo": cargo,
                            "cpf": cpf,
                            "nivel_acesso": int(nivel),
                            "email": email,
                            "ativo": ativo,
                        },
                    )
                    registrar_mensagem_crud(msg)
                    st.rerun()

    with remover:
        if not df.empty:
            registro_id = st.selectbox("Funcionario para remover", df["id"].tolist(), key="del_func")
            if st.button("Remover funcionario"):
                msg = remover_registro(Funcionario, int(registro_id))
                registrar_mensagem_crud(msg)
                st.rerun()

def exibir_crud_pessoas(modelo_nome):
    modelo = Procurado if modelo_nome == "Procurados" else PessoaComum
    df = listar_procurados() if modelo_nome == "Procurados" else listar_pessoas_comuns()
    funcionarios = opcoes_funcionarios()

    st.subheader(modelo_nome)
    exibir_mensagem_crud()
    st.dataframe(df, use_container_width=True, hide_index=True)

    criar, editar, remover = st.tabs(["Inserir", "Alterar", "Remover"])
    with criar:
        with st.form(f"criar_{modelo_nome}"):
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF")
            dados = {"nome": nome, "cpf": cpf, "foto_base64": FOTO_EXEMPLO_BASE64}
            if modelo is Procurado:
                nivel = st.number_input("Nivel de periculosidade", min_value=1, max_value=5, value=3)
                dados["nivel_periculosidade"] = int(nivel)
            if funcionarios:
                selecionado = st.selectbox("Cadastrado por", list(funcionarios.keys()))
                dados["cadastrado_por"] = funcionarios[selecionado]
            foto = st.text_area("Foto em Base64 (opcional)", placeholder="Deixe vazio para usar uma imagem minima valida")
            if foto.strip():
                dados["foto_base64"] = foto.strip()

            if st.form_submit_button(f"Inserir {modelo_nome.lower()}"):
                msg = criar_registro(modelo, dados)
                registrar_mensagem_crud(msg)
                st.rerun()

    with editar:
        if not df.empty:
            registro_id = st.selectbox(f"{modelo_nome} para alterar", df["id"].tolist())
            atual = df[df["id"] == registro_id].iloc[0]
            with st.form(f"editar_{modelo_nome}"):
                nome = st.text_input("Nome", value=atual["nome"])
                cpf = st.text_input("CPF", value=atual["cpf"])
                dados = {"nome": nome, "cpf": cpf}
                if modelo is Procurado:
                    nivel_atual = int(atual["nivel_periculosidade"] or 1)
                    nivel = st.number_input(
                        "Nivel de periculosidade",
                        min_value=1,
                        max_value=5,
                        value=nivel_atual,
                    )
                    dados["nivel_periculosidade"] = int(nivel)
                if funcionarios:
                    selecionado = st.selectbox("Cadastrado por", list(funcionarios.keys()))
                    dados["cadastrado_por"] = funcionarios[selecionado]
                if st.form_submit_button("Salvar alteracoes"):
                    msg = atualizar_registro(modelo, int(registro_id), dados)
                    registrar_mensagem_crud(msg)
                    st.rerun()

    with remover:
        if not df.empty:
            registro_id = st.selectbox(f"{modelo_nome} para remover", df["id"].tolist(), key=f"del_{modelo_nome}")
            if st.button(f"Remover {modelo_nome.lower()}"):
                msg = remover_registro(modelo, int(registro_id))
                registrar_mensagem_crud(msg)
                st.rerun()

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

caminho_imagem = os.path.join(diretorio_atual,"assets" ,"safer-banner.svg")

try:
    with open(caminho_imagem, "r", encoding="utf-8") as f:
        svg_texto = f.read()
    
    st.image(svg_texto, use_container_width=True)

except FileNotFoundError:
    st.error(f"Erro: imagem não encontrada: {caminho_imagem}")

st.title("S.A.F.E.R. - Dashboard de Análise e Gerenciamento")
st.caption("Sistema de Análise Facial para Entidades de Risco")
st.markdown("---")

aba_selecionada = st.sidebar.radio(
    "Navegação",
    [
        "Visão Geral",
        "Dados de Segurança Pública",
        "Modelagem e Consultas SQL",
        "Sistema de Gerenciamento do Banco de Dados",
        "Busca no Sistema",
    ],
)

if aba_selecionada == "Visão Geral":
    st.header("Estatisticas do Sistema Interno")
    
    try:
        t_proc, t_func, t_comum, df_niveis = buscar_estatisticas_safer()

        col1, col2, col3 = st.columns(3)
        col1.metric("Procurados cadastrados", t_proc)
        col2.metric("Pessoas comuns no histórico", t_comum)
        col3.metric("Funcionários ativos", t_func)

        st.subheader("Distribuição por nível de periculosidade")
        if not df_niveis.empty:
            contagem = df_niveis["Nivel"].value_counts().reset_index()
            contagem.columns = ["Nivel de Periculosidade", "Quantidade"]
            contagem = contagem.sort_values(by="Nivel de Periculosidade")

            fig = px.bar(
                contagem,
                x="Quantidade",
                y="Nivel de Periculosidade",
                orientation="h",
                title="Procurados por nível",
            )
            fig.update_layout(yaxis={"type": "category"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado de periculosidade disponível.")

        st.subheader("Resumo da view de cadastros")
        try:
            df_view = pd.read_sql("SELECT * FROM vw_resumo_cadastros_safer", engine)
            st.dataframe(df_view, use_container_width=True, hide_index=True)
        except Exception:
            st.info("A view vw_resumo_cadastros_safer ainda nao foi criada. Use a aba Modelagem e Consultas SQL.")

    except Exception as e:
        st.error(f"Erro ao conectar com o banco do projeto: {e}")

elif aba_selecionada == "Dados de Segurança Pública":
    st.header("Análise de Dados Públicos de Segurança")

    fonte_dados = st.radio(
        "Fonte dos dados publicos",
        ["Banco de Dados (Tabela dados_seguranca_publica)"],
    )

    df_publico = None
    if fonte_dados == "Upload de Arquivo CSV":
        arquivo_csv = st.file_uploader("Carregue o arquivo BancoVDE2025.csv", type=["csv"])
        if arquivo_csv is not None:
            df_publico = pd.read_csv(arquivo_csv, sep=";", low_memory=False, decimal=",")
            st.success("CSV carregado com sucesso.")
    else:
        try:
            df_publico = carregar_dados_publicos_db()
            st.success("Dados carregados do banco MySQL local.")
        except Exception as e:
            st.warning(
                "A tabela dados_seguranca_publica nao foi encontrada ou a conexao falhou. "
                "Rode o script database/databaseDadosPublicos.py antes de usar esta opcao."
            )
            st.exception(e)

    if df_publico is not None and not df_publico.empty:
        df_publico = preparar_dados_publicos(df_publico)
        st.subheader("Amostra dos dados importados")
        st.dataframe(df_publico.head(15), use_container_width=True, hide_index=True)

        df_filtrado = aplicar_filtros_publicos(df_publico)
        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
        else:
            exibir_metricas_publicas(df_filtrado)
            exibir_graficos_publicos(df_filtrado)

            csv_exportado = df_filtrado.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Exportar dados filtrados",
                data=csv_exportado,
                file_name="analise_dados_publicos_safer.csv",
                mime="text/csv",
            )

elif aba_selecionada == "Modelagem e Consultas SQL":
    st.header("Modelo ER, Relações e Consultas")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Entidades do projeto")
        st.markdown(
            """
            - funcionarios(id, nome, cargo, cpf, nivel_acesso, email, senha_hash, ativo)
            - procurados(id, nome, cpf, nivel_periculosidade, foto_base64, data_cadastro, cadastrado_por)
            - pessoa_comum(id, nome, cpf, foto_base64, data_cadastro, cadastrado_por)
            - dados_seguranca_publica(uf, municipio, evento, data_referencia, agente, arma, faixa_etaria, feminino, masculino, nao_informado, total_vitima, total, total_peso, abrangencia)
            - vw_resumo_cadastros_safer(funcionario_id, funcionario, cargo, total_procurados_cadastrados, total_pessoas_comuns_cadastradas, maior_nivel_periculosidade_cadastrado)
            """
        )

    with col2:
        st.subheader("Relacionamentos")
        st.markdown(
            """
            - funcionarios 1:N procurados
            - funcionarios 1:N pessoa_comum
            - dados_seguranca_publica e uma tabela analitica importada de CSV publico para validar o contexto de seguranca publica do projeto
            - vw_resumo_cadastros_safer consolida os cadastros feitos por funcionario
            """
        )

    st.subheader("Criação da view")
    st.code(
        """
CREATE OR REPLACE VIEW vw_resumo_cadastros_safer AS
SELECT
    f.id AS funcionario_id,
    f.nome AS funcionario,
    f.cargo,
    COUNT(DISTINCT p.id) AS total_procurados_cadastrados,
    COUNT(DISTINCT pc.id) AS total_pessoas_comuns_cadastradas,
    MAX(p.nivel_periculosidade) AS maior_nivel_periculosidade_cadastrado
FROM funcionarios f
LEFT JOIN procurados p ON p.cadastrado_por = f.id
LEFT JOIN pessoa_comum pc ON pc.cadastrado_por = f.id
GROUP BY f.id, f.nome, f.cargo;
        """,
        language="sql",
    )
    if st.button("Criar ou atualizar view no MySQL"):
        try:
            criar_view_resumo()
            st.success("View criada/atualizada com sucesso.")
        except Exception as e:
            st.error(f"Erro ao criar a view: {e}")

    st.subheader("Consultas estatísticas para apresentação no dashboard")
    consultas = {
        "SUM/AVG/MAX/MIN por municipio": """
SELECT municipio,
       SUM(total_vitima) AS total_vitimas,
       AVG(total_vitima) AS media_vitimas,
       MAX(total_vitima) AS max_vitimas,
       MIN(total_vitima) AS min_vitimas
FROM dados_seguranca_publica
GROUP BY municipio
ORDER BY total_vitimas DESC
LIMIT 10;
        """,
        "Eventos mais recorrentes": """
SELECT evento, SUM(total_vitima) AS total_vitimas
FROM dados_seguranca_publica
GROUP BY evento
ORDER BY total_vitimas DESC;
        """,
        "Resumo da view de cadastros": "SELECT * FROM vw_resumo_cadastros_safer;",
    }
    consulta_nome = st.selectbox("Escolha uma consulta", list(consultas.keys()))
    st.code(consultas[consulta_nome], language="sql")
    if st.button("Executar consulta selecionada"):
        try:
            df_sql = pd.read_sql(consultas[consulta_nome], engine)
            st.dataframe(df_sql, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro ao executar consulta: {e}")

elif aba_selecionada == "Sistema de Gerenciamento do Banco de Dados":
    st.header("Consulta, Inserção, Alteração e Remoção pelo Dashboard")
    entidade = st.selectbox("Tabela para manipular", ["Procurados", "Pessoas Comuns", "Funcionários"])
    try:
        if entidade == "Funcionários":
            exibir_crud_funcionarios()
        else:
            exibir_crud_pessoas(entidade)
    except Exception as e:
        st.error(f"Erro ao acessar a tabela selecionada: {e}")

elif aba_selecionada == "Busca no Sistema":
    st.header("Busca de Procurados")

    termo = st.text_input(
        "Digite o nome ou CPF do procurado",
        placeholder="Ex: Kennymar ou 222.222.222-22",
    )

    if st.button("Buscar"):
        if termo:
            resultados_df = buscar_procurados(termo)
            if not resultados_df.empty:
                st.success(f"{len(resultados_df)} registro(s) encontrado(s).")
                st.dataframe(resultados_df, hide_index=True, use_container_width=True)
            else:
                st.warning("Nenhum registro encontrado com esses termos.")
        else:
            st.info("Digite um termo para realizar a busca.")
