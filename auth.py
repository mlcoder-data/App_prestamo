import streamlit as st

def login():
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario:
        return True

    usuarios_autorizados = {
        "Mateo": "Almacen123",
        "Juliana": "abcd"
    }

    # === Estilos CSS ===
    st.markdown("""
        <style>
        .login-outer-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 35vh;
        }

        .main-title {
            font-size: 2.5rem;
            color: #ffffff;
            background-color: #00cc66;
            padding: 0.8rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }

        .login-box {
            background-color: #1e1e1e;
            padding: 2rem 3rem;
            border-radius: 12px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }

        .login-title {
            background-color: #00cc66;
            padding: 0.6rem;
            color: white;
            text-align: center;
            border-radius: 8px;
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            font-weight: bold;
        }

        .stTextInput > div > div > input {
            border-radius: 8px !important;
            padding: 0.5rem;
        }

        .stButton > button {
            width: 100%;
            border-radius: 8px;
            background-color: #00cc66;
            font-weight: bold;
        }

        .stButton > button:hover {
            background-color: #00994d;
        }
        </style>

        <div class="login-outer-container">
            <div class="main-title">🗂️ CONTROL DE INVENTARIO</div>
            <div class="login-box">
                <div class="login-title">🔐 Inicio de sesión</div>
    """, unsafe_allow_html=True)

    # === Campos de inicio de sesión ===
    usuario = st.text_input("Usuario", key="usuario_input")
    contraseña = st.text_input("Contraseña", type="password", key="password_input")

    if st.button("Iniciar sesión"):
        if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == contraseña:
            st.session_state.usuario = usuario
            st.success(f"Sesión iniciada como {usuario}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == contraseña:
        st.session_state.usuario = usuario
        st.session_state.is_admin = True if usuario in ["Mateo", "Juliana"] else False
        st.success(f"Sesión iniciada como {usuario}")
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
    return False
