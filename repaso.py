import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from gdrive_storage import descargar_csv, subir_csv, listar_tareas_csv

def repaso_menu():
    # === Configuración ===
    DATA_FOLDER = "data"
    PERIODOS = {
        "muy_dificil": 1,
        "dificil": 3,
        "facil": 7
    }
    DIFICULTADES = ["muy_dificil", "dificil", "facil"]

    # === Utilidades ===
    def calcular_siguiente_revision(fecha_str, dificultad):
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            return datetime.today()
        return fecha + timedelta(days=PERIODOS.get(dificultad, 1))

    def aumentar_dificultad(actual):
        idx = DIFICULTADES.index(actual)
        if idx < len(DIFICULTADES) - 1:
            return DIFICULTADES[idx + 1]
        return actual

    def disminuir_dificultad(actual):
        idx = DIFICULTADES.index(actual)
        if idx > 0:
            return DIFICULTADES[idx - 1]
        return actual

    # === Streamlit ===
    st.title("📖 Sesión de repaso")

    # Paso 1: Selección de tarea
    tareas = listar_tareas_csv()
    if not tareas:
        st.warning("No hay tareas disponibles para repasar.")
        st.stop()

    tarea = st.selectbox("Selecciona una tarea para repasar", tareas)
    nombre_fichero = f"{tarea}.csv"

    # Paso 2: Cargar datos
    try:
        df = descargar_csv(nombre_fichero)
    except FileNotFoundError:
        st.error("No se pudo cargar el archivo de la tarea.")
        st.stop()

    if df.empty:
        st.info("La tarea no tiene elementos aún.")
        st.stop()

    # Paso 3: Calcular ítems pendientes
    hoy = datetime.today()
    pendientes = []

    for idx, fila in df.iterrows():
        fecha_rev = fila.get("fecha_ultima_revision", "01/01/1970")
        proxima = calcular_siguiente_revision(fecha_rev, fila["dificultad"])
        if proxima <= hoy:
            pendientes.append(idx)

    if not pendientes:
        st.success("No hay elementos pendientes de repasar hoy.")
        st.stop()

    # Paso 4: Formulario de repaso
    st.subheader("🔁 Elementos pendientes de repaso")

    respuestas = {}

    with st.form("form_repaso"):
        for idx in pendientes:
            fila = df.loc[idx]
            st.markdown(f"**{fila['objetivo']}** → _{fila['resultado']}_")
            respuesta = st.radio(
                f"¿Recordado el elemento {idx+1}?",
                ["Sí", "No"],
                key=f"repaso_{idx}"
            )
            respuestas[idx] = respuesta
        submitted = st.form_submit_button("Actualizar tarea")

    # Paso 5: Actualizar según respuesta
    if submitted:
        for idx, respuesta in respuestas.items():
            if respuesta == "Sí":
                # Se recuerda: mantener dificultad, avanzar fecha
                dificultad = df.loc[idx, "dificultad"]
            else:
                # No se recuerda: subir dificultad o mantener y reiniciar
                dificultad = disminuir_dificultad(df.loc[idx, "dificultad"])

            df.loc[idx, "dificultad"] = dificultad
            df.loc[idx, "fecha_ultima_revision"] = hoy.strftime("%d/%m/%Y")

        # Guardar cambios
        os.makedirs(DATA_FOLDER, exist_ok=True)
        ruta_local = os.path.join(DATA_FOLDER, nombre_fichero)
        df.to_csv(ruta_local, index=False)
        subir_csv(ruta_local, nombre_fichero)

        st.success("Tarea actualizada correctamente.")
        st.rerun()
        
if __name__ == "__main__":
    repaso_menu()