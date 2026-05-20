import dropbox
import streamlit as st

cols_censurar = ["CPF"]
cols_esconder = ["Usuário"]
preenchimento_automatico = ["Usuário", "Data", "CPF", "encaminhamento conforme grade de referência?", "hospital final"]

APP_KEY = st.secrets["APP_KEY"]
APP_SECRET = st.secrets["APP_SECRET"]
REFRESH_TOKEN = st.secrets["REFRESH_TOKEN"]

ARQUIVO_DF = "/planilha monitoramento.xlsx"
ARQUIVO_LOGIN = "/login_senha.txt"
ARQUIVO_PDR = "/pdr.xlsx"
ARQUIVO_GRADE = "/grade.xlsx"

dbx = dropbox.Dropbox(
    oauth2_refresh_token=REFRESH_TOKEN,
    app_key=APP_KEY,
    app_secret=APP_SECRET
)

def gerar_box(pdr, grade):
    return {
    "autuação para quem? (geral/específica)": ["geral", "específica"],
    "município de origem": pdr["municipios_formatados"].tolist(),
    "hospitais encaminhados": grade["Hospital (caso houver)"].unique().tolist(),
    "Acompanhamento RAPS? (se sim, colocar o município)": ["-"] + pdr["municipios_formatados"].tolist()
}
