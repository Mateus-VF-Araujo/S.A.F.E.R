import base64
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from dashconfig.estilo import html_arte_vertical
from database.models import Funcionario, PessoaComum, Procurado
from facial.model_stream import analisar_foto_streamlit

DATABASE_URL = os.getenv(
    "SAFER_DATABASE_URL",
    "mysql+pymysql://root:root@localhost:3306/safer_db",
)

FOTO_EXEMPLO_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwAD"
    "hgGAWjR9awAAAABJRU5ErkJggg=="
)


def codificar_imagem_para_base64(arquivo_ou_caminho) -> str:
    if hasattr(arquivo_ou_caminho, "read"):
        bytes_imagem = arquivo_ou_caminho.read()
    else:
        bytes_imagem = Path(arquivo_ou_caminho).read_bytes()
    return base64.b64encode(bytes_imagem).decode("utf-8")


def disparar_bip_sonoro():

    audio_url = "https://actions.google.com/sounds/v1/alarms/spaceship_alarm.ogg"

    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="{audio_url}" type="audio/ogg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


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
                "Foto_Base64": p.foto_base64,
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
            df["data_referencia"], dayfirst=True, errors="coerce"
        )
        df["mes_referencia"] = df["data_referencia"].dt.to_period("M").astype(str)

    for coluna in [
        "uf",
        "municipio",
        "evento",
        "agente",
        "arma",
        "faixa_etaria",
        "abrangencia",
    ]:
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
                title="Evolução Mensal com Linhas de Análise",
            )

            import numpy as np

            x_num = np.arange(len(serie))
            y_valores = serie["total_vitima"].values

            if len(x_num) > 1:
                coeficientes = np.polyfit(x_num, y_valores, 1)
                reta_tendencia = np.poly1d(coeficientes)(x_num)

                fig.add_scatter(
                    x=serie["mes_referencia"],
                    y=reta_tendencia,
                    mode="lines",
                    name="Linha de Tendência",
                    line=dict(color="red", dash="dash"),
                )

            media_geral = serie["total_vitima"].mean()
            fig.add_hline(
                y=media_geral,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"Média: {int(media_geral)}",
                annotation_position="bottom right",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("A coluna data_referencia não está disponível para série temporal.")

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            colunas_genero = [
                c for c in ["feminino", "masculino", "nao_informado"] if c in df.columns
            ]
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
                    title="Armas - maior total de vítimas",
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
                    title="Agentes - maior total registrado",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

    with tab5:
        dimensao = st.selectbox(
            "Agrupar estatísticas por",
            [
                c
                for c in ["municipio", "evento", "arma", "agente", "faixa_etaria", "uf"]
                if c in df.columns
            ],
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
        f.id AS funcionario_id, f.nome AS funcionario, f.cargo,
        COUNT(DISTINCT p.id) AS total_procurados_cadastrados,
        COUNT(DISTINCT pc.id) AS total_pessoas_comuns_cadastradas,
        MAX(p.nivel_periculosidade) AS maior_nivel_periculosidade_cadastrado
    FROM funcionarios f
    LEFT JOIN procurados p ON p.cadastrado_por = f.id
    LEFT JOIN pessoa_comum pc ON pc.cadastrado_por = f.id
    GROUP BY f.id, f.nome, f.cargo
    """
    executar_sql(query)


def exibir_crud_funcionarios(nivel_usuario, cargo_usuario):
    st.subheader("Funcionarios")
    exibir_mensagem_crud()
    df = listar_funcionarios()
    st.dataframe(df, use_container_width=True, hide_index=True)

    pode_editar_remover = (nivel_usuario >= 5) or (
        str(cargo_usuario).lower() == "administrador"
    )
    pode_inserir = (nivel_usuario >= 4) or pode_editar_remover

    abas_nomes = []
    if pode_inserir:
        abas_nomes.append("Inserir")
    if pode_editar_remover:
        abas_nomes.append("Alterar")
        abas_nomes.append("Remover")

    if not abas_nomes:
        st.warning("Seu usuário não possui permissão para modificar Funcionários.")
        return

    abas = st.tabs(abas_nomes)
    idx_aba = 0

    if "Inserir" in abas_nomes:
        with abas[idx_aba]:
            with st.form("criar_funcionario"):
                nome = st.text_input("Nome")
                cargo = st.text_input("Cargo", value="Analista de Seguranca")
                cpf = st.text_input("CPF")
                nivel = st.number_input(
                    "Nivel de acesso", min_value=1, max_value=5, value=2
                )
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
        idx_aba += 1

    if "Alterar" in abas_nomes:
        with abas[idx_aba]:
            if not df.empty:
                registro_id = st.selectbox(
                    "Funcionario para alterar", df["id"].tolist()
                )
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
        idx_aba += 1

    if "Remover" in abas_nomes:
        with abas[idx_aba]:
            if not df.empty:
                registro_id = st.selectbox(
                    "Funcionario para remover", df["id"].tolist(), key="del_func"
                )
                if st.button("Remover funcionario"):
                    msg = remover_registro(Funcionario, int(registro_id))
                    registrar_mensagem_crud(msg)
                    st.rerun()


def exibir_crud_pessoas(modelo_nome, nivel_usuario, cargo_usuario, id_usuario_logado):
    modelo = Procurado if modelo_nome == "Procurados" else PessoaComum
    df = listar_procurados() if modelo_nome == "Procurados" else listar_pessoas_comuns()

    st.subheader(modelo_nome)
    exibir_mensagem_crud()

    colunas_para_mostrar = [c for c in df.columns if c != "Foto_Base64"]
    st.dataframe(df[colunas_para_mostrar], use_container_width=True, hide_index=True)

    cargo_formatado = str(cargo_usuario).lower()
    pode_editar_remover = (nivel_usuario >= 5) or (cargo_formatado == "administrador")

    pode_inserir = (
        (nivel_usuario >= 4)
        or pode_editar_remover
        or (cargo_formatado == "cadastrador")
    )

    abas_nomes = []
    if pode_inserir:
        abas_nomes.append("Inserir")
    if pode_editar_remover:
        abas_nomes.append("Alterar")
        abas_nomes.append("Remover")

    if not abas_nomes:
        st.warning(
            "Seu usuário não possui permissão para modificar cadastros de pessoas."
        )
        return

    abas = st.tabs(abas_nomes)
    idx_aba = 0

    if "Inserir" in abas_nomes:
        with abas[idx_aba]:
            with st.form(f"criar_{modelo_nome}"):
                nome = st.text_input("Nome")
                cpf = st.text_input("CPF")

                dados = {
                    "nome": nome,
                    "cpf": cpf,
                    "foto_base64": FOTO_EXEMPLO_BASE64,
                    "cadastrado_por": id_usuario_logado,
                }

                if modelo is Procurado:
                    nivel = st.number_input(
                        "Nivel de periculosidade", min_value=1, max_value=5, value=3
                    )
                    dados["nivel_periculosidade"] = int(nivel)

                foto_arquivo = st.file_uploader(
                    "Foto da Pessoa (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"]
                )

                if st.form_submit_button(f"Inserir {modelo_nome.lower()}"):
                    if foto_arquivo is not None:
                        dados["foto_base64"] = codificar_imagem_para_base64(
                            foto_arquivo
                        )

                    msg = criar_registro(modelo, dados)
                    registrar_mensagem_crud(msg)
                    st.rerun()
        idx_aba += 1

    if "Alterar" in abas_nomes:
        with abas[idx_aba]:
            if not df.empty:
                registro_id = st.selectbox(
                    f"{modelo_nome} para alterar", df["id"].tolist()
                )
                atual = df[df["id"] == registro_id].iloc[0]
                with st.form(f"editar_{modelo_nome}"):
                    nome = st.text_input("Nome", value=atual["nome"])
                    cpf = st.text_input("CPF", value=atual["cpf"])

                    dados = {
                        "nome": nome,
                        "cpf": cpf,
                        "cadastrado_por": id_usuario_logado,
                    }

                    if modelo is Procurado:
                        nivel_atual = int(atual["nivel_periculosidade"] or 1)
                        nivel = st.number_input(
                            "Nivel de periculosidade",
                            min_value=1,
                            max_value=5,
                            value=nivel_atual,
                        )
                        dados["nivel_periculosidade"] = int(nivel)

                    foto_arquivo_edicao = st.file_uploader(
                        "Atualizar Foto",
                        type=["png", "jpg", "jpeg"],
                        key=f"edit_foto_{modelo_nome}",
                    )

                    if st.form_submit_button("Salvar alteracoes"):
                        if foto_arquivo_edicao is not None:
                            dados["foto_base64"] = codificar_imagem_para_base64(
                                foto_arquivo_edicao
                            )

                        msg = atualizar_registro(modelo, int(registro_id), dados)
                        registrar_mensagem_crud(msg)
                        st.rerun()
        idx_aba += 1

    if "Remover" in abas_nomes:
        with abas[idx_aba]:
            if not df.empty:
                registro_id = st.selectbox(
                    f"{modelo_nome} para remover",
                    df["id"].tolist(),
                    key=f"del_{modelo_nome}",
                )
                if st.button(f"Remover {modelo_nome.lower()}"):
                    msg = remover_registro(modelo, int(registro_id))
                    registrar_mensagem_crud(msg)
                    st.rerun()


def telaLogin():
    st.markdown("<br><br>", unsafe_allow_html=True)

    col_margem_esq, col_login, col_arte, col_margem_dir = st.columns(
        [1, 3, 3, 1], gap="large"
    )

    with col_login:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #ffffff; letter-spacing: 4px; font-weight: 700; margin: 0;">LOGIN</h2>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            cpf_ou_email = st.text_input(
                "CPF ou E-mail",
                placeholder="CPF ou E-mail",
                label_visibility="collapsed",
            )
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Senha",
                label_visibility="collapsed",
            )

            btn_entrar = st.form_submit_button("ENTRAR", use_container_width=True)

            if btn_entrar:
                with SessionLocal() as session:
                    usuario = (
                        session.query(Funcionario)
                        .filter(
                            (Funcionario.email == cpf_ou_email)
                            | (Funcionario.cpf == cpf_ou_email)
                        )
                        .first()
                    )

                    if usuario and usuario.senha_hash == senha:
                        if usuario.ativo:
                            st.session_state["logado"] = True
                            st.session_state["usuario_dados"] = {
                                "id": usuario.id,
                                "nome": usuario.nome,
                                "cargo": usuario.cargo,
                                "nivel_acesso": int(usuario.nivel_acesso),
                            }
                            st.rerun()
                        else:
                            st.error(
                                "Usuário inativo. Procure o administrador do sistema."
                            )
                    else:
                        st.error("Credenciais inválidas.")

    with col_arte:
        st.markdown(html_arte_vertical, unsafe_allow_html=True)


def exibir_camera_reconhecimento():
    st.header("Painel Operacional de Monitoramento")
    st.info("Sistema de câmera do agente ativado.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Reconhecimento Facial")

        foto_capturada = st.camera_input("Câmera de Monitoramento")

        if foto_capturada is not None:
            bytes_foto = foto_capturada.getvalue()

            with st.spinner("Analisando biometria facial na rede neural..."):
                resultados = analisar_foto_streamlit(bytes_foto)

                if not resultados:
                    st.warning(
                        "Nenhum rosto foi detectado na imagem. Tente novamente em um ambiente mais iluminado."
                    )
                else:
                    match = resultados[0]

                    match_status = match.get("status")
                    match_nome = match.get("full_name", "Desconhecido")
                    match_cpf = match.get("cpf", "---")

                    nivel_perigo = match.get("risk_level", 5)

                    if match_status == "unknown":
                        st.error("Pessoa não localizada na base de dados.")
                        st.warning(
                            "Deseja cadastrá-la agora na base biométrica? Acesse a aba de Gerenciamento."
                        )

                    elif match_status == "wanted_alert":
                        disparar_bip_sonoro()
                        st.toast("ALERTA: Alvo de Risco Identificado!", icon="🚨")

                        with st.container(border=True):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                # Tenta buscar a foto do banco
                                foto_banco = match.get("foto")
                                if foto_banco:
                                    try:
                                        dados_foto = base64.b64decode(foto_banco)
                                        st.image(
                                            dados_foto,
                                            use_container_width=True,
                                            caption="Foto do Registro",
                                        )
                                    except Exception:
                                        st.image(
                                            bytes_foto,
                                            use_container_width=True,
                                            caption="Foto da Câmera",
                                        )
                                else:
                                    st.image(
                                        bytes_foto,
                                        use_container_width=True,
                                        caption="Foto da Câmera",
                                    )
                            with c2:
                                st.markdown("### 🔴 PROCURADO IDENTIFICADO")
                                st.markdown(f"**Nome:** {match_nome}")
                                st.markdown(f"**CPF:** {match_cpf}")
                                st.markdown(
                                    f"**Nível de Periculosidade:** {nivel_perigo}"
                                )
                                st.markdown("**Localização:** Câmera Frontal do Agente")

                        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        st.session_state["historico_alertas"].insert(
                            0,
                            {
                                "data": agora,
                                "nome": match_nome,
                                "nivel": str(nivel_perigo),
                                "local": "Câmera Frontal do Agente",
                            },
                        )

                    elif match_status == "employee_authorized":
                        st.success(
                            f" Funcionário Autorizado: {match_nome} (CPF: {match_cpf}). Acesso Liberado."
                        )

                    elif match_status == "common_cleared":
                        st.success("Verificação de Segurança Concluída")

                        with st.container(border=True):
                            c1, c2 = st.columns([1, 2])

                            with c1:
                                foto_banco = match.get("foto")
                                if foto_banco:
                                    try:
                                        dados_foto = base64.b64decode(foto_banco)
                                        st.image(
                                            dados_foto,
                                            use_container_width=True,
                                            caption="Foto do Registro",
                                        )
                                    except Exception:
                                        st.image(
                                            bytes_foto,
                                            use_container_width=True,
                                            caption="Foto da Câmera",
                                        )
                                else:
                                    st.image(
                                        bytes_foto,
                                        use_container_width=True,
                                        caption="Foto da Câmera",
                                    )

                            with c2:
                                st.markdown("### 🟢 PESSOA NÃO PROCURADA")
                                st.markdown(f"**Nome:** {match_nome}")
                                st.markdown(f"**CPF:** {match_cpf}")
                                st.markdown(
                                    "**Status:** Indivíduo sem mandados ou restrições ativas no sistema."
                                )

    with col2:
        st.subheader("Histórico de Notificações")
        if st.session_state.get("historico_alertas"):
            df_hist = pd.DataFrame(st.session_state["historico_alertas"])
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.write("Nenhum alerta crítico registrado nesta sessão.")


def exibir_busca_sistema_customizada():
    st.header("Consulta de Procurados")
    termo = st.text_input(
        "Digite o nome ou CPF para pesquisa",
        placeholder="Ex: Kennymar ou 222.222.222-22",
    )

    if termo:
        resultados_df = buscar_procurados(termo)
        if not resultados_df.empty:
            st.success(f"{len(resultados_df)} registro(s) encontrado(s).")
            st.markdown("---")

            for _, row in resultados_df.iterrows():
                with st.container(border=True):
                    col_foto, col_info = st.columns([1, 4])

                    with col_foto:
                        if row.get("Foto_Base64") and row["Foto_Base64"] != "Sem foto":
                            try:
                                dados_foto = base64.b64decode(row["Foto_Base64"])
                                st.image(dados_foto, use_container_width=True)
                            except Exception:
                                st.error("Erro ao processar imagem da base de dados.")
                        else:
                            st.caption("Sem registro fotográfico")

                    with col_info:
                        st.markdown(f"## {row['Nome']}")
                        st.markdown(f"**CPF:** {row['CPF']}")

                        nivel = row["Nivel Periculosidade"]
                        cor_nivel = "🔴" if nivel >= 4 else "🟡" if nivel == 3 else "🟢"
                        st.markdown(f"**Nível de Periculosidade:** {nivel} {cor_nivel}")
                        st.caption(
                            f"ID do Registro: {row['ID']} | Data de Entrada: {row['Data Cadastro']}"
                        )
        else:
            st.warning("Nenhum registro encontrado com estes parâmetros.")
