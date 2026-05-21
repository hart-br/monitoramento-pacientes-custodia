import streamlit as st
import pandas as pd
from config import preenchimento_automatico

class Forms:
    def __init__(self, box):
        self.data = ["Data", "data da internação", "data da alta médica", "data de envio do caso para juiz articulador",
             "data da decisão judicial  expressa da cessação da internação", "data da desospitalização do paciente"]
        self.simples = ["Nome do paciente"]
        self.expand = ["Observações (sinalizar fatores como dificuldades de infraestrutura, de negativa de hospitais etc.)"]
        self.box = box
        self.especial = ["hospitais encaminhados"]
        self.frase_1_hosp = "Qual o primeiro hospital que tentaram encaminhar o paciente?"
        self.frase_hosp = "Qual foi o próximo hospital encaminhado?"
        self.frase_aceito = "O paciente foi aceito no hospital?"
        self.opcoes_box = opcoes_box = ["", "sim", "não"]

    def gerar_cols(self, cpf, df, existence):
        cols = [x for x in df.columns if x not in preenchimento_automatico]
        linha = df[df["CPF"] == cpf].reset_index()
        hospital_final = linha.at[0, "hospital final"]
        nova_linha = {}

        for col in [x for x in cols if x not in preenchimento_automatico]:
            st.write("")
            if col in self.box:
                if col in self.especial:
                    st.warning("Para cada hospital recusado, surgirá um novo campo para preencher o próximo hospital")
                    hospitais = []

                    #Se já existir hospitais com ou sem recusa
                    if existence and pd.notna(linha.iloc[0][col]):
                        valor_atual = linha.iloc[0][col]
                        hospitais_cp = [x.split() for x in valor_atual.split(", ") if x.split() != "-"]

                        #Placeholders para controlar iterações
                        n_hospital = 300 #valor aleatorio so para distinguir do n_aceito
                        n_aceito = 0

                        for i, hospital_cp in enumerate(hospitais_cp):
                            n_hospital += 1
                            n_aceito += 1

                            #Pergunta do hospital
                            if i == 0:
                                hospitais.append(st.selectbox(self.frase_1_hosp, self.box[col],
                                                              index=self.box[col].index(hospitais_cp[i]), key=n_hospital))
                            else:
                                hospitais.append(st.selectbox(self.frase_hosp, self.box[col],
                                                              index=self.box[col].index(hospitais_cp[i]), key=n_hospital))
                            st.write("")

                            #Pergunta do aceite
                            if hospital_cp == hospital_final:
                                aceito = st.selectbox(self.frase_aceito, self.opcoes_box, index=1, key=n_aceito)
                                fim = aceito != "não"
                            elif i < len(hospitais_cp) - 1:
                                aceito = st.selectbox(self.frase_aceito, self.opcoes_box, index=2, key=n_aceito)
                            else:
                                aceito = st.selectbox(self.frase_aceito, self.opcoes_box, key=n_aceito)
                                fim = aceito != "não"
                            st.write("")

                    #Se não existir hospitais cadastrados ainda
                    else:
                        n_hospital = 300
                        n_aceito = 0

                        hospitais.append(st.selectbox(self.frase_1_hosp, self.box[col], key=n_hospital))
                        aceito = st.selectbox(self.frase_aceito, self.opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    while not fim:
                        n_hospital += 1
                        n_aceito += 1
                        hospitais.append(st.selectbox(self.frase_hosp, self.box[col], key=n_hospital))
                        aceito = st.selectbox(self.frase_aceito, self.opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    nova_linha[col] = ", ".join([x.split() for x in hospitais if x.split() != "-"])
                    st.write("")

                elif existence and pd.notna(linha.iloc[0][col]):
                    valor_atual = linha.iloc[0][col]
                    nova_linha[col] = st.selectbox(col, self.box[col], index=self.box[col].index(valor_atual))
                else:
                    nova_linha[col] = st.selectbox(col, self.box[col])


            elif col in self.data:
                if existence and pd.notna(linha.iloc[0][col]):
                    data = st.date_input(f"{col} (Selecionar no calendário)",
                                                    value=pd.to_datetime(linha.iloc[0][col],
                                                                         dayfirst=True).date())
                else:
                    data = st.date_input(f"{col} (Selecionar no calendário)", value=None)

                nova_linha[col] = data
                if data is not None:
                    nova_linha[col] = data.strftime("%d/%m/%Y")


            elif col in self.simples:
                if existence and pd.notna(linha.iloc[0][col]):
                    nova_linha[col] = st.text_input(col, value=linha.iloc[0][col])
                else:
                    nova_linha[col] = st.text_input(col)

            elif col in self.expand:
                if existence and pd.notna(linha.iloc[0][col]):
                    nova_linha[col] = st.text_area(col, value=linha.iloc[0][col])
                else:
                    nova_linha[col] = st.text_area(col)

        return nova_linha, aceito == "sim"
