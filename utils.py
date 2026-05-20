import pandas as pd
import streamlit as st
import re
import requests
from io import BytesIO
from config import cols_censurar, cols_esconder

class Utils:
    def __init__(self, pdr, grade, storage):
        self.pdr = pdr
        self.grade = grade
        self.storage = storage

    def verificar_internet(self):
        try:
            requests.get("https://www.google.com", timeout=2)
        except (requests.ConnectionError, requests.Timeout):
            st.error("Sem conexão com a internet. Conecte-se à internet e atualize a página.")
            st.stop()

    def censurar(self, df):
        df = df.copy()
        for col in df.columns:
            if col in cols_censurar:
                df[col] = "[CENSURADO]"
        return df.drop(cols_esconder, axis=1)

    def validar_cpf(self, cpf):
        return bool(re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf))

    def verificar_existencia_cpf(self, df, cpf):
        values = df["CPF"].values.tolist()
        if cpf in values:
            return True, values.index(cpf)
        else:
            return False, None

    def verificar_colunas_para_grade(self, paciente):
        if paciente.get("município de origem") and paciente.get("hospitais encaminhados") and paciente.get("hospitais encaminhados") != "-":
            return True
        return False

    def verificar_encaminhamento_grade(self, paciente):
        hospital = [x for x in paciente["hospitais encaminhados"].split(", ")][0]
        origem = paciente["município de origem"]
        grade = self.grade.copy()
        grade = grade[grade["Hospital (caso houver)"] == hospital]
        referenciados = []
        for municipio in grade["Municipios Referenciados "].dropna():
            referenciados.extend([y.strip() for y in municipio.split(",")])
        return origem in referenciados

    def completar_paciente(self, paciente, cpf):
        paciente["CPF"] = cpf
        paciente["Data"] = self.storage.pegar_data()
        paciente["Usuário"] = st.session_state.usuario
        paciente["hospital final"] = [x for x in paciente["hospitais encaminhados"].split(", ")][-1]
        if self.verificar_colunas_para_grade(paciente):
            grade_bool = self.verificar_encaminhamento_grade(paciente)
            if grade_bool:
                paciente["encaminhamento conforme grade de referência?"] = "Sim"
            else:
                paciente["encaminhamento conforme grade de referência?"] = "Não"
        else:
            paciente["encaminhamento conforme grade de referência?"] = "Sem informações"
        return paciente

    def converter_df_para_xlsx(self, df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output.getvalue()
