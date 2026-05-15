import streamlit as st
import pandas as pd
import dropbox
from io import BytesIO
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from unidecode import unidecode
import time
from datetime import date

# =========================================
# VARIÁVEIS
# =========================================
cols_censurar = ["CPF", "usuario"]
preenchimento_automatico = ["usuario", "data_informacao", "CPF"]

# =========================================
# CONFIG
# =========================================

APP_KEY = st.secrets["APP_KEY"]
APP_SECRET = st.secrets["APP_SECRET"]
REFRESH_TOKEN = st.secrets["REFRESH_TOKEN"]

dbx = dropbox.Dropbox(
    oauth2_refresh_token=REFRESH_TOKEN,
    app_key=APP_KEY,
    app_secret=APP_SECRET
)

ARQUIVO_DROPBOX = "/Planilha de monitoramento paciente audiência custodia - Página1.xlsx"
ARQUIVO_LOGIN = "/login_senha.txt"
ARQUIVO_PDR = "/PDR_2024.xlsx"
ARQUIVO_GRADE = "/grade.xlsx"

@st.cache_data
def pegar_texto():
    metadata, response = dbx.files_download(ARQUIVO_LOGIN)
    return unidecode(response.content.decode("utf-8"))
texto = pegar_texto()

login_senha = dict(
    re.findall(
        r"usuario:\s*(\S+)\s*[\r\n]+senha:\s*(\S+)",
        texto,
        flags=re.IGNORECASE
    )
)

match = re.search(
    r"usuario_admin:\s*(\S+)\s*[\r\n]+senha_admin:\s*(\S+)",
    texto,
    flags=re.IGNORECASE
)

admin_login = match.group(1)
admin_senha = match.group(2)

# =========================================
# FUNÇÕES
# =========================================

@st.cache_data
def carregar_df(ARQUIVO_DROPBOX):
    metadata, response = dbx.files_download(ARQUIVO_DROPBOX)
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


def deduplicar_alteracoes(df):
    return df.drop_duplicates()

def verificar_internet():
    try:
        requests.get("https://www.google.com", timeout=2)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def salvar_dataframe(nova_linha, ARQUIVO_DROPBOX, cpf_existente):
    if not verificar_internet():
        st.error("Erro: sem conexão com a internet. Conecte-se à internet e tente novamente.")
        return False

    else:
        df = carregar_df(ARQUIVO_DROPBOX)
        nova_linha = pd.DataFrame([nova_linha])

        if cpf_existente:
            indice = df[df["CPF"] == nova_linha.iloc[0]["CPF"]].index[0]
            for col, valor in nova_linha.iloc[0].items():
                df.at[indice, col] = valor

        else:
            df = pd.concat([df, nova_linha], ignore_index=True)

        excel_buffer = BytesIO()

        df.to_excel(excel_buffer,index=False,engine="openpyxl",index_label=False)

        excel_buffer.seek(0)
        dbx.files_upload(
            excel_buffer.getvalue(),
            ARQUIVO_DROPBOX,
            mode=dropbox.files.WriteMode.overwrite
        )

        carregar_df.clear()
        return True

def pegar_data():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")

def censurar(df):
    df = df.copy()
    for col in df.columns:
        if col in cols_censurar:
            df[col] = "(CENSURADO)"
    return df

def converter_df_para_xlsx(df):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Planilha")

    buffer.seek(0)
    return buffer

# =========================================
# LOGIN E SETTING INICIAL
# =========================================

st.set_page_config("Monitoramento RAPS")

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.admin = False

if not st.session_state.logado:
    st.session_state.usuario = st.text_input("Digite seu login")
    st.session_state.senha = st.text_input("Digite sua senha", type="password")

    if not st.session_state.usuario or not st.session_state.senha:
        st.stop()

    elif st.session_state.usuario == admin_login and st.session_state.senha == admin_senha:
        st.success("Bem-vindo(a), administrador(a). Carregando...")
        st.session_state.logado = True
        st.session_state.admin = True
        time.sleep(1.5)
        st.rerun()

    elif st.session_state.usuario and st.session_state.senha and not (st.session_state.usuario in login_senha):
        st.error("Usuário e/ou senha inválido(s)")
        st.stop()

    elif st.session_state.usuario in login_senha and st.session_state.senha == login_senha[st.session_state.usuario]:
        for _ in range(3):
            st.write()
        st.success("Sucesso! Carregando...")
        st.session_state.logado = True
        time.sleep(1.5)
        st.rerun()

    else:
        st.error("Usuário e/ou senha inválido(s)")
        st.stop()


# =========================================
# IMPORTAR PLANILHAS
# =========================================

if not verificar_internet():
    st.error("Sem conexão com a internet. Conecte-se à internet e atualize a página.")
    st.stop()

df = carregar_df(ARQUIVO_DROPBOX)
pdr = carregar_df(ARQUIVO_PDR)
grade = carregar_df(ARQUIVO_GRADE)

box = {
    "autuação para quem?": ["município", "estado"],
    "município de origem": pdr["Município "].tolist(),
    "encaminhou para qual hospital?": grade["Hospital (caso houver)"].unique().tolist(),
}

# =========================================
# INTERFACE
# =========================================

st.title("Monitoramento de pacientes - custódia")

if not st.session_state.admin:
    aba1, aba2 = st.tabs(["planilha geral", "adicionar novo paciente"])

else:
    aba1, aba2, aba3 = st.tabs(["planilha geral", "adicionar novo paciente", "Informações para ADM"])

with aba1:
    st.header("Planilha completa")
    st.dataframe(censurar(df))
    st.info("Para fins de privacidade, o CPF dos pacientes foram censurados.")

with aba2:
    st.info("Digite um CPF válido (formatado como 000.000.000-00) e aperte enter. Se houver informações cadastradas, elas serão recuperadas")
    cpf = st.text_input("CPF")
    if cpf:
        cpf_valido = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf)

        if cpf_valido:
            cols = [x for x in df.columns if x not in preenchimento_automatico]
            nova_linha = {}

            cpf_existente = False
            if cpf in df["CPF"].tolist():
                cpf_existente = True
                linha = df[df["CPF"] == cpf]
                st.success("Paciente localizado. Recuperando dados...")
            else:
                st.info("Paciente ainda não cadastrado. Favor inserir dados.")


            for col in cols:

                if col in box:
                    if cpf_existente and pd.notna(linha.iloc[0][col]):
                        valor_atual = linha.iloc[0][col]
                        nova_linha[col] = st.selectbox(col, box[col], index=box[col].index(valor_atual))
                    else:
                        nova_linha[col] = st.selectbox(col, box[col])

                elif "data" in col:
                    if cpf_existente and pd.notna(linha.iloc[0][col]):
                        nova_linha[col] = st.date_input(f"{col} (Selecionar no calendário)", value=pd.to_datetime(linha.iloc[0][col], dayfirst=True).date()).strftime("%d/%m/%Y")
                    else:
                        nova_linha[col] = st.date_input(f"{col} (Selecionar no calendário)", value=date.today()).strftime("%d/%m/%Y")

                else:
                    if cpf_existente and pd.notna(linha.iloc[0][col]):
                        nova_linha[col] = st.text_input(col, value=linha.iloc[0][col])
                    else:
                        nova_linha[col] = st.text_input(col)

            if st.button("salvar e anexar na planilha as informações"):
                st.info("Aguarde, salvando...")
                nova_linha["data_informacao"] = pegar_data()
                nova_linha["usuario"] = st.session_state.usuario
                nova_linha["CPF"] = cpf
                if salvar_dataframe(nova_linha, ARQUIVO_DROPBOX ,cpf_existente):
                    st.success("Salvo com sucesso! Atualizando planilha...")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.error("CPF inválido. Tente novamente.")

if st.session_state.admin:
    with aba3:
        st.info("Espaço para administradores deste sistema (apenas CESMAD)")
        st.dataframe(df)

        arquivo_xlsx = converter_df_para_xlsx(df)

        st.download_button(
            label="Baixar planilha em Excel",
            data=arquivo_xlsx,
            file_name="planilha_monitoramento.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
