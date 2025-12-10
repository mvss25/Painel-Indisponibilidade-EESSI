import pandas as pd
import streamlit as st
from datetime import datetime

# ---------- CONFIGURAÇÃO DE AUTENTICAÇÃO ----------
SENHA_CORRETA = "Segurançasocial"  # 🔑 ALTERE PARA SUA SENHA!

def verificar_login():
    # Inicializa o estado de login se não existir
    if "logado" not in st.session_state:
        st.session_state.logado = False

    # Se não estiver logado, mostra o formulário de login
    if not st.session_state.logado:
        st.title("🔒 Acesso Restrito")
        senha = st.text_input("Digite a senha para acessar o painel:", type="password")
        if st.button("Entrar"):
            if senha == SENHA_CORRETA:
                st.session_state.logado = True  # ✅ Corrigido aqui!
                st.rerun()  # Recarrega a página para mostrar o painel
            else:
                st.error("Senha incorreta. Tente novamente.")
        st.stop()  # Impede o resto do código de rodar

# Verifica login antes de carregar o painel
verificar_login()
# ---------- A PARTIR DAQUI, O USUÁRIO ESTÁ AUTENTICADO ----------
st.set_page_config(layout="wide")
st.title("📊 Painel de Indisponibilidade de Ambientes")

# Opção de logout (opcional, na barra lateral)
with st.sidebar:
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

# Carregar Excel
try:
    df = pd.read_excel("indisponibilidades.xlsx", dtype=str)
    if df.empty:
        st.info("Nenhuma indisponibilidade registrada no arquivo Excel.")
        st.stop()
    
    df['Inicio'] = pd.to_datetime(df['Data Início'] + ' ' + df['Hora Início'])
    df['Fim'] = pd.to_datetime(df['Data Fim'] + ' ' + df['Hora Fim'])
    
except Exception as e:
    st.error(f"Erro ao carregar o Excel: {e}")
    st.stop()

agora = datetime.now()

# Checkbox para histórico
mostrar_historico = st.checkbox("✅ Mostrar histórico completo (incluindo indisponibilidades passadas)")

# Filtrar
if mostrar_historico:
    df_exibicao = df.copy()
    titulo_tabela = "Todas as indisponibilidades (histórico completo)"
else:
    df_exibicao = df[df['Fim'] >= agora].copy()
    df_exibicao = df_exibicao.sort_values('Inicio')
    titulo_tabela = "Próximas indisponibilidades"

# Formatar datas
df_exibicao['Inicio_fmt'] = df_exibicao['Inicio'].dt.strftime('%d/%m/%Y %H:%M')
df_exibicao['Fim_fmt'] = df_exibicao['Fim'].dt.strftime('%d/%m/%Y %H:%M')

# Status atual
df_exibicao['Status Atual'] = df_exibicao.apply(
    lambda row: "🔴 Em andamento" if row['Inicio'] <= agora <= row['Fim'] 
                else ("🟢 Futura" if row['Inicio'] > agora else "⚪ Concluída"),
    axis=1
)

# Tabela principal
st.subheader(titulo_tabela)
if df_exibicao.empty:
    st.info("Nenhuma indisponibilidade para exibir com os filtros atuais.")
else:
    tabela = df_exibicao[['Ambiente', 'Inicio_fmt', 'Fim_fmt', 'Motivo', 'Status', 'Status Atual']]
    tabela.columns = ['Ambiente', 'Início', 'Fim', 'Motivo', 'Status', 'Status Atual']
    st.dataframe(tabela, use_container_width=True, hide_index=True)

# Indisponibilidades em andamento
st.markdown("---")
st.subheader("🚨 Indisponibilidades em andamento")
em_andamento = df[(df['Inicio'] <= agora) & (df['Fim'] >= agora)].copy()
if not em_andamento.empty:
    em_andamento['Inicio_fmt'] = em_andamento['Inicio'].dt.strftime('%d/%m/%Y %H:%M')
    em_andamento['Fim_fmt'] = em_andamento['Fim'].dt.strftime('%d/%m/%Y %H:%M')
    st.warning("⚠️ Há ambientes indisponíveis no momento!")
    st.dataframe(
        em_andamento[['Ambiente', 'Inicio_fmt', 'Fim_fmt', 'Motivo', 'Status']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ Todos os ambientes estão disponíveis no momento.")

# Resumo na barra lateral
st.sidebar.markdown("### 📈 Resumo")
total = len(df)
ativas = len(df[df['Fim'] >= agora])
em_andamento_count = len(em_andamento)
historico = total - ativas

st.sidebar.metric("Total registrado", total)
st.sidebar.metric("Ativas (futuras ou em andamento)", ativas)
st.sidebar.metric("Em andamento", em_andamento_count)
st.sidebar.metric("Histórico (concluídas)", historico)