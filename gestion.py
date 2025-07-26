import streamlit as st
import pandas as pd
import os
from datetime import datetime
from gdrive_storage import descargar_csv, subir_csv, listar_tareas_csv

def gestion_menu():
    # === Configuración ===
    DATA_FOLDER = "data"
    CAMPOS = ["objetivo", "resultado", "dificultad", "fecha_ultima_revision"]

    st.title("📋 Gestión de tareas de memorización")

    # --- Paso 1: Selección o creación de tarea ---
    modo = st.radio("¿Qué deseas hacer?", ["Seleccionar tarea existente", "Crear nueva tarea"])

    if modo == "Seleccionar tarea existente":
        tareas = listar_tareas_csv()
        if not tareas:
            st.warning("No hay tareas disponibles aún.")
            st.stop()
        tarea = st.selectbox("Selecciona una tarea", tareas)
    else:
        tarea = st.text_input("Introduce el nombre de la nueva tarea (sin espacios):").strip()
        if not tarea:
            st.info("Introduce un nombre para la nueva tarea.")
            st.stop()

    # --- Paso 2: Cargar datos ---
    nombre_fichero = f"{tarea}.csv"
    try:
        df = descargar_csv(nombre_fichero)
    except FileNotFoundError:
        df = pd.DataFrame(columns=CAMPOS)

    # --- Paso 3: Control de reseteo de campos (antes de renderizar widgets) ---
    if "form_reset" not in st.session_state:
        st.session_state.form_reset = False
    if "objetivo" not in st.session_state:
        st.session_state.objetivo = ""
    if "resultado" not in st.session_state:
        st.session_state.resultado = ""
    if "dificultad" not in st.session_state:
        st.session_state.dificultad = "dificil"

    if st.session_state.form_reset:
        st.session_state.objetivo = ""
        st.session_state.resultado = ""
        st.session_state.dificultad = "dificil"
        st.session_state.form_reset = False
        st.rerun()

    # --- Paso 4: Formulario controlado ---
    st.subheader("➕ Añadir nuevo elemento a la tarea")
    form_placeholder = st.empty()

    def mostrar_formulario(df_actual):
        with form_placeholder.form(key=f"form_nuevo_{tarea}"):
            objetivo = st.text_input("Frase o palabra objetivo", key="objetivo")
            resultado = st.text_input("Traducción esperada", key="resultado")
            dificultad = st.selectbox(
                "Nivel de dificultad",
                ["muy_dificil", "dificil", "facil"],
                #key="dificultad"
                index=1
            )
            submitted = st.form_submit_button("Guardar")

            if submitted:
                if not objetivo.strip() or not resultado.strip():
                    st.warning("Los campos objetivo y resultado no pueden estar vacíos.")
                else:
                    nueva_fila = {
                        "objetivo": objetivo.strip(),
                        "resultado": resultado.strip(),
                        "dificultad": dificultad,
                        "fecha_ultima_revision": datetime.today().strftime("%d/%m/%Y")
                    }
                    df_actual = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)

                    os.makedirs(DATA_FOLDER, exist_ok=True)
                    ruta_local = os.path.join(DATA_FOLDER, nombre_fichero)
                    df_actual.to_csv(ruta_local, index=False, encoding="utf-8")
                    subir_csv(ruta_local, nombre_fichero)

                    st.success("Elemento guardado correctamente.")
                    st.session_state.form_reset = True
                    st.rerun()

        return df_actual

    # --- Mostrar formulario y actualizar df ---
    df = mostrar_formulario(df)

    # --- Paso 5: Mostrar contenido actual (opcional) ---
    if not df.empty:
        if st.checkbox("📄 Mostrar tabla actual de la tarea"):
            st.dataframe(df)

if __name__ == "__main__":
    gestion_menu()