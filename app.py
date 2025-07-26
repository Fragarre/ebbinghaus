import streamlit as st

# === Importar funciones de cada módulo ===
from gestion import gestion_menu
from repaso import repaso_menu
from ejercicios import ejercicios_menu
from traduccion import traduccion_menu

# === Configuración general ===
st.set_page_config(page_title="📚 App Ebbinghaus", layout="wide")
st.title("🧠 Aplicación de Memorización basada en Ebbinghaus")

# === Navegación lateral ===
modulo = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Gestión de Tareas", "Repaso Diario", "Generar Ejercicios", "Traductor con Voz"]
)

# === Cargar el módulo seleccionado ===
if modulo == "Gestión de Tareas":
    gestion_menu()
elif modulo == "Repaso Diario":
    repaso_menu()
elif modulo == "Generar Ejercicios":
    ejercicios_menu()
elif modulo == "Traductor con Voz":
    traduccion_menu()
