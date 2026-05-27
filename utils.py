import dropbox
from unidecode import unidecode
import re
import pandas as pd
from io import BytesIO
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from config import (APP_KEY, APP_SECRET, REFRESH_TOKEN, ARQUIVO_GRADE, ARQUIVO_DF,
                    ARQUIVO_PDR, ARQUIVO_LOGIN)

class Storage:
    def __init__(self):
        self.dbx = dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN,
                                   app_key=APP_KEY,app_secret=APP_SECRET)

    @st.cache_data(show_spinner=False)
    def coletar_login(_self):
        metadata, response = _self.dbx.files_download(ARQUIVO_LOGIN)
        texto = unidecode(response.content.decode("utf-8"))

        login_normal = dict(re.findall(r"usuario:\s*(\S+)\s*[\r\n]+senha:\s*(\S+)",
                                       texto,flags=re.IGNORECASE))

        match_admin = re.search(
            r"usuario_admin:\s*(\S+)\s*[\r\n]+senha_admin:\s*(\S+)",
            texto,
            flags=re.IGNORECASE
        )

        login_admin = (match_admin.group(1), match_admin.group(2))

        return login_normal, login_admin

    @st.cache_data(show_spinner=False)
    def carregar_df(_self):
        metadata, response = _self.dbx.files_download(ARQUIVO_DF)
        return pd.read_excel(BytesIO(response.content), engine="openpyxl", dtype=str)

    @st.cache_data(show_spinner=False)
    def carregar_arquivos(_self):
        metadata, response = _self.dbx.files_download(ARQUIVO_PDR)
        pdr = pd.read_excel(BytesIO(response.content), engine="openpyxl")

        metadata, response = _self.dbx.files_download(ARQUIVO_GRADE)
        grade = pd.read_excel(BytesIO(response.content), engine="openpyxl", sheet_name="Grade")

        return pdr, grade

    def pegar_data(_self):
        return datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")

    def salvar_df(self, paciente, cpf, utils, existence, hospital_fim, grade):
        paciente = utils.completar_paciente(paciente, cpf, hospital_fim, grade)

        self.carregar_df.clear()
        df = self.carregar_df()
        paciente = pd.DataFrame([paciente])

        if existence:
            indice = df[df["CPF"] == paciente.iloc[0]["CPF"]].index[0]
            for col, valor in paciente.iloc[0].items():
                df.at[indice, col] = valor

        else:
            df = pd.concat([df, paciente], ignore_index=True)

        excel = utils.converter_df_para_xlsx(df)

        self.dbx.files_upload(excel, ARQUIVO_DF, mode=dropbox.files.WriteMode.overwrite)
        self.carregar_df.clear()
        return True
