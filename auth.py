import streamlit as st
import time

class Auth:
    def __init__(self, login_senha, login_senha_admin):
        self.login_senha = login_senha
        self.login_senha_admin = login_senha_admin

    def sucesso(self):
        st.session_state.logado = True
        time.sleep(1)
        st.rerun()

    def logar(self):
        #Verificar logado ou admin
        if "admin" in st.session_state:
            if st.session_state.admin:
                return True
        st.session_state.admin = False

        if "logado" in st.session_state:
            if st.session_state.logado:
                return True
        st.session_state.logado = False

        #Iniciar sistema de login
        admin_user = self.login_senha_admin[0]
        admin_senha = self.login_senha_admin[1]

        st.title("AUTENTICAÇÃO")
        for _ in range(2):
            st.write("")

        st.session_state.usuario = st.text_input("Digite seu usuário")
        st.session_state.senha = st.text_input("Digite sua senha", type="password")

        usuario = st.session_state.usuario
        senha = st.session_state.senha

        if st.button("Entrar"):
            if usuario == admin_user and senha == admin_senha:
                st.success("Bem-vindo(a), administrador(a). Carregando...")
                st.session_state.admin = True
                self.sucesso()

            if usuario in self.login_senha and senha == self.login_senha[usuario]:
                st.success("Sucesso! Carregando...")
                self.sucesso()

            st.error("Usuário e/ou senha inválido(s)")
            return False
