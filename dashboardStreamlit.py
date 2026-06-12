import pandas as pd
import plotly.express as px
import streamlit as st

import dashconfig.funtionsDash as dash_funcs
from dashconfig.estilo import fonte_e_grade_css, html_estrutura

st.set_page_config(layout="wide", page_title="S.A.F.E.R. Dashboard")

st.markdown(fonte_e_grade_css, unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["usuario_dados"] = None

if "historico_alertas" not in st.session_state:
    st.session_state["historico_alertas"] = []

if not st.session_state["logado"]:
    dash_funcs.telaLogin()

else:
    st.markdown(html_estrutura, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    nivel_usuario = st.session_state["usuario_dados"]["nivel_acesso"]
    cargo_usuario = st.session_state["usuario_dados"]["cargo"]
    id_usuario_logado = st.session_state["usuario_dados"]["id"]

    st.sidebar.markdown(
        f"👤 **Bem-vindo(a), {st.session_state['usuario_dados']['nome']}**"
    )

    if st.sidebar.button("Sair do Sistema"):
        st.session_state["logado"] = False
        st.session_state["usuario_dados"] = None
        st.rerun()

    st.sidebar.markdown("---")

    # Controle de Acesso das Abas
    if nivel_usuario == 1:
        abas_disponiveis = [
            "Câmera de Reconhecimento Facial",
            "Dados de Segurança Pública",
            "Busca no Sistema",
        ]
    else:
        abas_disponiveis = [
            "Visão Geral",
            "Câmera de Reconhecimento Facial",
            "Dados de Segurança Pública",
            "Modelagem e Consultas SQL",
            "Sistema de Gerenciamento do Banco de Dados",
            "Busca no Sistema",
        ]

    aba_selecionada = st.sidebar.radio("Navegação", abas_disponiveis)

    if aba_selecionada == "Câmera de Reconhecimento Facial":
        dash_funcs.exibir_camera_reconhecimento()

    elif aba_selecionada == "Visão Geral":
        st.header("Estatisticas do Sistema Interno")
        try:
            t_proc, t_func, t_comum, df_niveis = dash_funcs.buscar_estatisticas_safer()
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
                df_view = pd.read_sql(
                    "SELECT * FROM vw_resumo_cadastros_safer", dash_funcs.engine
                )
                st.dataframe(df_view, use_container_width=True, hide_index=True)
            except Exception:
                st.info(
                    "A view vw_resumo_cadastros_safer ainda nao foi criada. Use a aba Modelagem e Consultas SQL."
                )
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
            arquivo_csv = st.file_uploader(
                "Carregue o arquivo BancoVDE2025.csv", type=["csv"]
            )
            if arquivo_csv is not None:
                df_publico = pd.read_csv(
                    arquivo_csv, sep=";", low_memory=False, decimal=","
                )
                st.success("CSV carregado com sucesso.")
        else:
            try:
                df_publico = dash_funcs.carregar_dados_publicos_db()
                st.success("Dados carregados do banco MySQL local.")
            except Exception as e:
                st.warning(
                    "A tabela dados_seguranca_publica nao foi encontrada ou a conexao falhou."
                )
                st.exception(e)

        if df_publico is not None and not df_publico.empty:
            df_publico = dash_funcs.preparar_dados_publicos(df_publico)
            st.subheader("Amostra dos dados importados")
            st.dataframe(df_publico.head(15), use_container_width=True, hide_index=True)

            df_filtrado = dash_funcs.aplicar_filtros_publicos(df_publico)
            if df_filtrado.empty:
                st.warning("Nenhum registro encontrado com os filtros selecionados.")
            else:
                dash_funcs.exibir_metricas_publicas(df_filtrado)
                dash_funcs.exibir_graficos_publicos(df_filtrado)

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
                - funcionarios N:N procurados
                - funcionarios N:N pessoa_comum
                - dados_seguranca_publica e uma tabela analitica importada de CSV publico
                - vw_resumo_cadastros_safer consolida os cadastros feitos por funcionario
                """
            )

        st.subheader("Criação da view")
        st.code(
            """
    CREATE OR REPLACE VIEW vw_resumo_cadastros_safer AS
    SELECT
        f.id AS funcionario_id, f.nome AS funcionario, f.cargo,
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
                dash_funcs.criar_view_resumo()
                st.success("View criada/atualizada com sucesso.")
            except Exception as e:
                st.error(f"Erro ao criar a view: {e}")

        st.subheader("Consultas estatísticas")
        consultas = {
            "SUM/AVG/MAX/MIN por municipio": "SELECT municipio, SUM(total_vitima) AS total_vitimas, AVG(total_vitima) AS media_vitimas, MAX(total_vitima) AS max_vitimas, MIN(total_vitima) AS min_vitimas FROM dados_seguranca_publica GROUP BY municipio ORDER BY total_vitimas DESC LIMIT 10;",
            "Eventos mais recorrentes": "SELECT evento, SUM(total_vitima) AS total_vitimas FROM dados_seguranca_publica GROUP BY evento ORDER BY total_vitimas DESC;",
            "Resumo da view de cadastros": "SELECT * FROM vw_resumo_cadastros_safer;",
        }
        consulta_nome = st.selectbox("Escolha uma consulta", list(consultas.keys()))
        st.code(consultas[consulta_nome], language="sql")
        if st.button("Executar consulta selecionada"):
            try:
                df_sql = pd.read_sql(consultas[consulta_nome], dash_funcs.engine)
                st.dataframe(df_sql, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Erro ao executar consulta: {e}")

    elif aba_selecionada == "Sistema de Gerenciamento do Banco de Dados":
        st.header("Sistema de Gerenciamento do Banco de Dados")
        entidade = st.selectbox(
            "Tabela para manipular", ["Procurados", "Pessoas Comuns", "Funcionários"]
        )

        try:
            if entidade == "Funcionários":
                dash_funcs.exibir_crud_funcionarios(nivel_usuario, cargo_usuario)
            else:
                dash_funcs.exibir_crud_pessoas(
                    entidade, nivel_usuario, cargo_usuario, id_usuario_logado
                )
        except Exception as e:
            st.error(f"Erro ao acessar a tabela selecionada: {e}")

    elif aba_selecionada == "Busca no Sistema":
        dash_funcs.exibir_busca_sistema_customizada()
