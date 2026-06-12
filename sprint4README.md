# Sprint 4: Autenticação e Autorização

Como o sistema é construído sobre o Streamlit (onde o script é reexecutado a cada iteração do usuário), a segurança foi garantida utilizando dependências no `st.session_state` e roteamento dinâmico.

## Autenticação

A Autenticação é o processo de verificação da identidade do usuário. O sistema exige validação cruzada contra o banco de dados MySQL via SQLAlchemy.

Apenas funcionários cadastrados e com a flag `ativo = True` conseguem gerar uma sessão válida. Quando as credenciais (CPF/E-mail e Senha) são confirmadas, o sistema injeta os dados operacionais do funcionário na sessão e força o recarregamento da página para liberar a interface.

**Implementação no código (`funtionsDash.py`):**
```python
btn_entrar = st.form_submit_button("ENTRAR", use_container_width=True)

if btn_entrar:
    with SessionLocal() as session:
        # Permite login tanto por E-mail quanto por CPF
        usuario = (
            session.query(Funcionario)
            .filter(
                (Funcionario.email == cpf_ou_email)
                | (Funcionario.cpf == cpf_ou_email)
            )
            .first()
        )
        # Validação da identidade e do status da conta
        if usuario and usuario.senha_hash == senha:
            if usuario.ativo:
                st.session_state["logado"] = True
                st.session_state["usuario_dados"] = {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "cargo": usuario.cargo,
                    "nivel_acesso": int(usuario.nivel_acesso),
                }
                st.rerun() # Limpa a tela de login e monta a área restrita
            else:
                st.error(
                    "Usuário inativo. Procure o administrador do sistema."
                )
        else:
            st.error("Credenciais inválidas.")
```

## Autorização em Níveis de Acesso 

A Autorização é o mecanismo que dita quais funcionalidades um usuário logado pode acessar. No S.A.F.E.R., isso foi implementado através de uma arquitetura de privilégios condicionais baseada no `nivel_acesso` do funcionário.

Isso significa que o nível do usuário funciona como a chave para liberar ou ocultar ferramentas do painel, garantindo que Agentes de Campo não manipulem o banco de dados.

### Acesso a telas do Dashboards
O menu lateral é construído em tempo real de acordo com o nível do funcionário. Agentes (Nível 1) visualizam um menu restrito focado no monitoramento biométrico.

**Implementação no código (`dashboardStreamlit.py`):**
```python
nivel_usuario = st.session_state["usuario_dados"]["nivel_acesso"]

# Controle de Acesso das Abas baseado no nível
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
```

### Autorização de inserção, alteração e exclusão
Além de bloquear páginas inteiras, o sistema bloqueia ações específicas dentro das páginas. Na área de Gerenciamento do Banco de Dados, as abas de "Inserir", "Alterar" e "Remover" só são montadas e exibidas na tela se o usuário cumprir os requisitos de nível lógico para aquela tabela.

**Implementação no código (`funtionsDash.py`):**
```python

def exibir_crud_funcionarios(nivel_usuario, cargo_usuario):
    st.subheader("Funcionarios")

    exibir_mensagem_crud()

    df = listar_funcionarios()
    
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Autorização baseada em cargo e nível numérico
    pode_editar_remover = (nivel_usuario >= 5) or (
        str(cargo_usuario).lower() == "administrador"
    )
    pode_inserir = (nivel_usuario >= 4) or pode_editar_remover

    # Opções disponíveis para o usuário
    abas_nomes = []
    if pode_inserir:
        abas_nomes.append("Inserir")
    if pode_editar_remover:
        abas_nomes.append("Alterar")
        abas_nomes.append("Remover")

    # Caso o usuario tenha um nível de acesso menor 
    if not abas_nomes:
        st.warning("Seu usuário não possui permissão para modificar Funcionários.")
        return
```

Dessa forma, o S.A.F.E.R. garante não apenas que o indivíduo é quem diz ser (Autenticação), mas fortalece a integridade do banco de dados ao liberar ações específicas apenas para altos níveis de permissão (Autorização).