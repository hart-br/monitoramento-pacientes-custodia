import streamlit as st
import pandas as pd
from config import preenchimento_automatico

opcoes_box = ["", "sim", "não"]

class Forms:
    def __init__(self, box):
        self.data = ["Data", "data da internação", "data da alta médica", "data de envio do caso para juiz articulador",
             "data da decisão judicial  expressa da cessação da internação", "data da desospitalização do paciente"]
        self.simples = ["Nome do paciente"]
        self.expand = ["Observações (sinalizar fatores como dificuldades de infraestrutura, de negativa de hospitais etc.)"]
        self.box = box
        self.especial = ["hospitais encaminhados"]

    def gerar_cols(self, cpf, df, existence):
        cols = [x for x in df.columns if x not in preenchimento_automatico]
        linha = df[df["CPF"] == cpf]
        nova_linha = {}

        for col in [x for x in cols if x not in preenchimento_automatico]:
            st.write("")
            if col in self.box:
                if col in self.especial:

                    hospitais = []

                    if existence and pd.notna(linha.iloc[0][col]):
                        valor_atual = linha.iloc[0][col]
                        hospitais_cp = [x for x in valor_atual.split(", ")]

                        #Placeholders para controlar iterações
                        n_hospital = 300 #valor aleatorio so para distinguir do n_aceito
                        n_aceito = 0

                        for i, hospital_cp in enumerate(hospitais_cp):
                            n_hospital += 1
                            n_aceito += 1

                            if i == len(hospitais_cp) -1:
                                hospitais.append(
                                    st.selectbox("Qual foi o próximo hospital encaminhado?",
                                                 self.box[col], index=self.box[col].index(hospitais_cp[i]), key=n_hospital))
                                aceito = st.selectbox("O paciente foi aceito no hospital?", opcoes_box, key=n_aceito)
                                fim = aceito != "não"
                                st.write("")

                            elif i == 0:
                                hospitais.append(st.selectbox("Qual o primeiro hospital que o paciente foi encaminhado?",
                                                              self.box[col], index=self.box[col].index(hospitais_cp[i]), key=n_hospital))
                                aceito = st.selectbox("O paciente foi aceito no hospital?", opcoes_box, index=2, key=n_aceito)
                                st.write("")

                            else:
                                hospitais.append(st.selectbox("Qual foi o próximo hospital encaminhado?",
                                                 self.box[col], index=self.box[col].index(hospitais_cp[i]), key=n_hospital))
                                aceito = st.selectbox("O paciente foi aceito no hospital?", opcoes_box, index=2, key=n_aceito)
                                st.write("")


                    else:
                        n_hospital = 300
                        n_aceito = 0

                        hospitais.append(st.selectbox("Qual o primeiro hospital que o paciente foi encaminhado?", self.box[col], key=n_hospital))
                        aceito = st.selectbox("O paciente foi aceito no hospital?", opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    while not fim:
                        n_hospital += 1
                        n_aceito += 1
                        hospitais.append(st.selectbox("Qual foi o próximo hospital encaminhado?", self.box[col], key=n_hospital))
                        aceito = st.selectbox("O paciente foi aceito no hospital?", opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    nova_linha[col] = ", ".join(hospitais)


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
