import streamlit as st
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ejercicios_menu():

    # load_dotenv()
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.title("🧠 Ejercicios de traducción")

    # --- Parámetros del ejercicio ---
    idioma = st.selectbox("Selecciona el idioma", ["ingles", "frances", "italiano"])
    dificultad = st.selectbox("Selecciona la dificultad", ["fácil", "difícil", "muy difícil"])
    num_ejercicios = st.slider("Número de ejercicios", min_value=3, max_value=10, value=5)

    @st.cache_data(show_spinner=False)
    def generar_frases(idioma, dificultad, n):
        prompt = f"""
        Crea {n} frases en {idioma}, nivel {dificultad}, que un estudiante de español debería traducir al español.
        Devuélvelas en una lista de Python, sin explicaciones.
        """
        respuesta = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        lista = respuesta.choices[0].message.content.strip()
        try:
            return eval(lista)
        except:
            return [f"Error al generar frases: {lista}"]

    def comparar_traducciones(user_translation: str, target_translation: str, threshold: float = 0.88) -> bool:
        if not user_translation.strip() or not target_translation.strip():
            return False
        emb1 = client.embeddings.create(input=user_translation, model="text-embedding-3-small").data[0].embedding
        emb2 = client.embeddings.create(input=target_translation, model="text-embedding-3-small").data[0].embedding

        similitud = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return similitud >= threshold

    # --- Ejecución del ejercicio ---
    if st.button("Generar ejercicios"):
        frases = generar_frases(idioma, dificultad, num_ejercicios)
        respuestas = []

        st.session_state.frases = frases
        st.session_state.respuestas = ["" for _ in frases]

    if "frases" in st.session_state:
        st.subheader("Traduce las siguientes frases al español")
        with st.form(key="formulario_ejercicios"):
            for i, frase in enumerate(st.session_state.frases):
                st.markdown(f"**{i+1}. {frase}**")
                respuesta = st.text_input("Tu traducción:", key=f"respuesta_{i}")
                st.session_state.respuestas[i] = respuesta
            corregir = st.form_submit_button("Corregir")

        if corregir:
            st.subheader("Resultados")
            for i, (original, user_trad) in enumerate(zip(st.session_state.frases, st.session_state.respuestas)):
                prompt_correc = f"¿Cuál sería una traducción correcta al español de la siguiente frase en {idioma} (nivel {dificultad}): '{original}'?"
                respuesta = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt_correc}],
                    temperature=0.5
                )
                traduccion_correcta = respuesta.choices[0].message.content.strip()

                es_correcta = comparar_traducciones(user_trad, traduccion_correcta)

                st.markdown(f"**{i+1}. {original}**")
                st.markdown(f"✅ Tu respuesta: {user_trad}" if es_correcta else f"❌ Tu respuesta: {user_trad}")
                if not es_correcta:
                    st.markdown(f"Traducción sugerida: _{traduccion_correcta}_")

if __name__ == "__main__":
    ejercicios_menu()