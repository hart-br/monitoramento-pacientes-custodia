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

class Config:

    def gerar_box(self, pdr, grade):
        return {
    "autuação para quem? (geral/específica)": ["geral", "específica"],
    "município de origem": pdr["municipios_formatados"].tolist(),
    "hospitais encaminhados": grade["Hospital (caso houver)"].unique().tolist(),
    "Acompanhamento RAPS? (se sim, colocar o município)": ["-"] + pdr["municipios_formatados"].tolist()
}

    def definir_layout(self):
        st.markdown("""
        <style>

        /* ==========================
           FUNDO PRINCIPAL
        ========================== */
        .stApp {
            background: linear-gradient(
                135deg,
                #0F172A 0%,
                #1E293B 50%,
                #334155 100%
            );
        }

        /* ==========================
           TÍTULOS
        ========================== */
        h1, h2, h3 {
            color: #F8FAFC !important;
            font-weight: 700;
        }

        /* Texto normal */
        p, label {
            color: #E2E8F0 !important;
        }

        /* ==========================
           INPUTS
        ========================== */
        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input {
            background-color: rgba(255,255,255,0.94) !important;
            color: #111827 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
        }

        /* Selectbox */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(255,255,255,0.94) !important;
            color: #111827 !important;
            border-radius: 12px !important;
        }

        /* Placeholder */
        input::placeholder,
        textarea::placeholder {
            color: #6B7280 !important;
        }

        /* ==========================
           TABELAS
        ========================== */
        [data-testid="stDataFrame"] {
            background-color: rgba(230, 230, 230, 0.92) !important;
            border-radius: 16px !important;
            padding: 8px;
        }

        [data-testid="stDataFrame"] div {
            color: #111827 !important;
        }

        [data-testid="stDataFrame"] thead tr th {
            background-color: #D1D5DB !important;
            color: #111827 !important;
            font-weight: 700 !important;
        }

        [data-testid="stDataFrame"] tbody tr {
            background-color: rgba(240,240,240,0.95) !important;
        }

        [data-testid="stDataFrame"] tbody tr:hover {
            background-color: rgba(220,220,220,0.95) !important;
        }

        /* ==========================
           REMOVER CARD GLOBAL BUGADO
        ========================== */
        div[data-testid="stVerticalBlock"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            backdrop-filter: none !important;
        }

        /* ==========================
           BOTÕES
        ========================== */
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
        }
        
        /* Forçar texto preto */
        .stButton > button *,
        .stDownloadButton > button *,
        .stButton > button span,
        .stDownloadButton > button span {
            color: #000000 !important;
        }
        
        /* Hover */
        .stButton > button:hover *,
        .stDownloadButton > button:hover * {
            color: #000000 !important;
        }

        /* ==========================
           SIDEBAR
        ========================== */
        section[data-testid="stSidebar"] {
            background-color: rgba(15,23,42,0.96);
        }

        </style>
        """, unsafe_allow_html=True)
