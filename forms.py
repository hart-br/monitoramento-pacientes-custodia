import streamlit as st
import pandas as pd
from config import preenchimento_automatico, hospitais_psi
from unidecode import unidecode

class Forms:
    def __init__(self, box):
        self.data = ["Data", "data da internação", "data da alta médica", "data de envio do caso para juiz articulador",
             "data da decisão judicial  expressa da cessação da internação", "data da desospitalização do paciente",
             "Data do encaminhamento para RAPS"]
        self.simples = ["Nome do paciente"]
        self.expand = ["Observações (sinalizar fatores como dificuldades de infraestrutura, de negativa de hospitais etc.)"]
        self.box = box
        self.especial = ["hospitais encaminhados"]
        self.frase_1_hosp = "Qual o primeiro hospital que tentaram encaminhar o paciente?"
        self.frase_hosp = "Qual foi o próximo hospital encaminhado?"
        self.frase_aceito = "O paciente foi aceito no hospital?"
        self.opcoes_box = ["", "sim", "não"]
        self.hospitais = self.box["hospitais encaminhados"] + hospitais_psi

    def gerar_cols(self, cpf, df, existence, storage):
        sucesso = True
        cols = [x for x in df.columns if x not in preenchimento_automatico]
        hospital_final = None
        if existence:
            linha = df[df["CPF"] == cpf].reset_index(drop=True)
            hospital_final = linha.at[0, "hospital final"]
        nova_linha = {}
        datas = []

        for col in cols:
            if col in preenchimento_automatico:
                continue
            st.write("")

            if col in ["Qual o tipo de serviço da RAPS?", "Data do encaminhamento para RAPS"]:
                if nova_linha["Acompanhamento RAPS? (se sim, colocar o município)"].lower() == "não":
                    nova_linha["Qual o tipo de serviço da RAPS?"] = None
                    nova_linha["Data do encaminhamento para RAPS"] = None
                    continue
                elif col == "Qual o tipo de serviço da RAPS?":
                    st.info("Foram criados abaixo campos novos para preenchimento sobre a RAPS")

            if col in self.box:
                if col in self.especial:
                    st.warning("Para cada hospital recusado, surgirá um novo campo para preencher o próximo hospital")
                    hospitais = []

                    #Se já existir hospitais com ou sem recusa
                    if existence and pd.notna(linha.iloc[0][col]):
                        valor_atual = linha.iloc[0][col]
                        hospitais_cp = [unidecode(x.strip().upper()) for x in valor_atual.split(", ") if x.strip() not in ["-", ""]]

                        #Placeholders para controlar iterações
                        n_hospital = 300 #valor aleatorio so para distinguir do n_aceito
                        n_aceito = 0

                        for i, hospital_cp in enumerate(hospitais_cp):
                            n_hospital += 1
                            n_aceito += 1

                            #Pergunta do hospital
                            if i == 0:
                                hospitais.append(st.selectbox(self.frase_1_hosp, self.hospitais,
                                                              index=self.hospitais.index(hospitais_cp[i]), key=n_hospital))
                            else:
                                hospitais.append(st.selectbox(self.frase_hosp, self.hospitais,
                                                              index=self.hospitais.index(hospitais_cp[i]), key=n_hospital))
                            st.write("")

                            #Pergunta do aceite
                            if hospital_cp == hospital_final and i == len(hospitais_cp) - 1:
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

                        hospitais.append(st.selectbox(self.frase_1_hosp, self.hospitais, key=n_hospital))
                        aceito = st.selectbox(self.frase_aceito, self.opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    while not fim:
                        n_hospital += 1
                        n_aceito += 1
                        hospitais.append(st.selectbox(self.frase_hosp, self.hospitais, key=n_hospital))
                        aceito = st.selectbox(self.frase_aceito, self.opcoes_box, key=n_aceito)
                        fim = aceito != "não"
                        st.write("")

                    hospitais = [x.strip() for x in hospitais if x.strip() != "-"]
                    if len(hospitais) > 0:
                        nova_linha[col] = ", ".join([x.strip() for x in hospitais])
                    else:
                        nova_linha[col] = None
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
                datas.append(data)

                #Checar data
                if data is not None:
                    if pd.to_datetime(data) > pd.to_datetime(storage.pegar_data(), dayfirst=True):
                        st.error("A data selecionada está no futuro. Escolha outra.")
                        sucesso = False
                    if len(datas) > 1:
                        idx_data = len(datas) - 1
                        if datas[idx_data-1] is None:
                            st.error("Favor preencher a data anterior antes de preencher esta.")
                            sucesso = False
                        elif data < datas[idx_data-1]:
                            st.error("Pela lógica do fluxo, esta data não pode ser menor que a do campo anterior. Favor ajustar.")
                            sucesso = False

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

            # Checar se RAPS está antes de desospitalização
            if col == "Acompanhamento RAPS? (se sim, colocar o município)":
                if nova_linha["Acompanhamento RAPS? (se sim, colocar o município)"].lower() != "não" and (
                    pd.isna(nova_linha["data da desospitalização do paciente"])):
                    st.error("O encaminhamento à RAPS ocorre depois da desospitalização. Favor preencher primeiro a data desta.")
                    sucesso = False

        hospital_fim = aceito == "sim"
        return nova_linha, hospital_fim, sucesso
