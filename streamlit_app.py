#Fazer imporetações
import streamlit as st
import time
from storage import Storage
from utils import Utils
from auth import Auth
from config import Config, preenchimento_automatico
from forms import Forms

# =========================================
# INICIAL
# =========================================

#Tela de carregamento
st.set_page_config("Monitoramento RAPS")
config = Config()
config.definir_layout()

placeholder = st.empty()
placeholder.info("Iniciando o sistema. Favor aguardar.")

#Inicializando robôs
storage = Storage()
login_senha, login_senha_admin = storage.coletar_login()
auth = Auth(login_senha, login_senha_admin)

#Setting inicial
placeholder.empty()
if not auth.logar():
    st.stop()

#Importando arquivos e iniciando últimos robôs
df = storage.carregar_df()
pdr, grade = storage.carregar_arquivos()
utils = Utils(pdr, grade, storage)
forms = Forms(config.gerar_box(pdr, grade))

# =========================================
# INTERFACE PRINCIPAL
# =========================================

st.markdown("<h1 style='text-align: center;'>Monitoramento de Pacientes - Custódia</h1>",
            unsafe_allow_html=True)

if not st.session_state.admin:
    aba1, aba2, aba3 = st.tabs(["planilha geral", "adicionar novo paciente", "seus pacientes"])

else:
    aba1, aba2, aba3, aba4, aba5 = st.tabs(["planilha geral", "adicionar novo paciente",
                                      "planilha completa (admin)", "relatório (admin)", "usuários e senhas (admin)"])

with aba1:
    st.markdown(
        "<h2 style='text-align: center;'>Planilha Geral</h2>",
        unsafe_allow_html=True
    )
    st.dataframe(utils.censurar(df))
    st.info("Para fins de privacidade, o CPF dos pacientes foram censurados.")

with aba2:
    st.markdown(
        "<h2 style='text-align: center;'>Cadastrar Novo Paciente</h2>",
        unsafe_allow_html=True
    )
    st.info("Digite um CPF válido (formatado como 000.000.000-00) e aperte enter. Se houver informações cadastradas, elas serão recuperadas")
    cpf = st.text_input("CPF")
    if cpf:
        if utils.validar_cpf(cpf):
            with st.spinner("pesquisando CPF..."):
                existence, idx = utils.verificar_existencia_cpf(df, cpf)
                if existence:
                    linha = df[df["CPF"] == cpf]
                    st.write("")
                    st.success("Paciente localizado. Recuperando dados...")
                    st.write("")
                else:
                    st.info("Paciente ainda não cadastrado. Favor inserir dados.")

            paciente, hospital_fim = forms.gerar_cols(cpf, df, existence)
            if st.button("salvar e anexar na planilha as informações"):
                with st.spinner("Aguarde, salvando..."):
                    storage.salvar_df(paciente, cpf, utils, existence, hospital_fim)
                st.success("Salvo com sucesso! Atualizando planilha...")
                time.sleep(0.5)
                st.rerun()

        else:
            st.error("CPF inválido. Tente novamente.")

if not st.session_state.admin:
    with aba3:
        st.markdown(
            "<h2 style='text-align: center;'>Verificar Informações Cadastradas</h2>",
            unsafe_allow_html=True
        )
        st.info("Verifique as informações dos seus pacientes aqui.")
        df_usuario = df[df["Usuário"] == st.session_state.usuario].reset_index(drop=True)
        if len(df_usuario) > 0:
            st.dataframe(df_usuario)
            st.write("As colunas abaixo são preenchidas automaticamente pelo sistema:")
            st.write(f"\"" + f"\", \"".join([x for x in preenchimento_automatico if x != "CPF"]) + f"\".")
        else:
            st.error("Seu usuário ainda não tem paciente cadastrado. Cadastre e retorne nesta aba.")

if st.session_state.admin:
    with aba3:
        st.markdown(
            "<h2 style='text-align: center;'>Planilha Completa</h2>",
            unsafe_allow_html=True
        )
        st.info("Espaço exclusivo para administradores do sistema 😎")
        filtro = st.multiselect("usuário/regional",df["Usuário"].dropna().unique().tolist())
        df_filtrada = df[df["Usuário"].isin(filtro)] if filtro else df.copy()
        st.dataframe(df_filtrada)
        st.download_button(label="Baixar planilha em Excel",
            data=utils.converter_df_para_xlsx(df_filtrada),
            file_name="planilha_monitoramento.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with aba4:
        st.markdown(
            "<h2 style='text-align: center;'>Relatórios</h2>",
            unsafe_allow_html=True
        )
        st.info("Espaço exclusivo para administradores do sistema 😎")
        st.info("Mas ainda em construção. Volte mais tarde 😓")

    with aba5:
        st.markdown(
            "<h2 style='text-align: center;'>Usuários e Senhas</h2>",
            unsafe_allow_html=True
        )
        st.info("Espaço exclusivo para administradores do sistema 😎")
        st.dataframe(utils.df_login(login_senha))
