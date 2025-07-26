import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from gtts import gTTS
from io import BytesIO

def traduccion_menu():
    # === Configuración ===
    #load_dotenv()
    #openai = OpenAI()
    openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    # === Pronunciación con gTTS ===
    def reproducir_pronunciacion(texto: str, idioma: str):
        if not texto.strip():
            st.warning("⚠️ Texto vacío. No se puede generar pronunciación.")
            return
        try:
            tts = gTTS(text=texto.strip(), lang=idioma)
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            st.audio(mp3_fp, format='audio/mp3')
        except ValueError as ve:
            st.error(f"Idioma no compatible con gTTS: {ve}")
        except Exception as e:
            st.error(f"Error al generar audio: {e}")

    # === Inicializar estados ===
    if "traduccion" not in st.session_state:
        st.session_state.traduccion = ""
    if "ejemplo" not in st.session_state:
        st.session_state.ejemplo = ""
    if "frase_original" not in st.session_state:
        st.session_state.frase_original = ""
    if "traduccion_reset" not in st.session_state:
        st.session_state.traduccion_reset = False

    # === Reset controlado del formulario ===
    if st.session_state.traduccion_reset:
        st.session_state.frase_original = ""
        st.session_state.traduccion = ""
        st.session_state.ejemplo = ""
        st.session_state.traduccion_reset = False
        st.rerun()

    # === Interfaz ===
    st.header("🌍 Traducción de frases con IA")

    idiomas_disponibles = ["francés", "inglés", "alemán", "italiano", "portugués"]
    idioma_codigos = {
        "francés": "fr",
        "inglés": "en",
        "alemán": "de",
        "italiano": "it",
        "portugués": "pt"
    }

    idioma = st.selectbox("Selecciona el idioma:", idiomas_disponibles, index = 1)
    codigo_idioma = idioma_codigos[idioma]

    direccion = st.radio(
        "Dirección de traducción:", 
        [f"Español → {idioma.capitalize()}", f"{idioma.capitalize()} → Español"],
        index = 1)

    st.text_area("Introduce la frase a traducir:", key="frase_original", height=100)

    # === Botón para limpiar ===
    if st.button("🧹 Limpiar frase"):
        st.session_state.traduccion_reset = True
        st.rerun()

    # === Botón para traducir ===
    if st.button("Traducir"):
        texto_original = st.session_state.frase_original.strip()

        if not texto_original:
            st.warning("Por favor, introduce una frase para traducir.")
        else:
            if direccion.startswith("Español"):
                prompt_usuario = (
                    f"Traduce del {idioma} al español. Frase: '{texto_original.strip()}'. "
                    f"Dame solo la traducción más natural y contextualizada en español, evitando traducciones literales. "
                    f"Luego, genera una frase en {idioma} (no en español) que use la frase original correctamente en contexto, sin decir que es un ejemplo. "
                    f"Dame primero la traducción, luego una línea en blanco, y luego la frase contextual."
                )
            else:
                prompt_usuario = (
                    f"Traduce del {idioma} al español. Frase: '{texto_original.strip()}'. "
                    f"Dame solo la traducción más natural y contextualizada en español, evitando traducciones literales. "
                    f"Luego, genera una frase en {idioma} que use la frase original correctamente en contexto. "
                    f"No digas que es un ejemplo. Dame primero la traducción, luego una línea en blanco, y luego la frase contextual en {idioma}."
                )

            try:
                respuesta = openai.chat.completions.create(
                    model="gpt-4",
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": (
                            "Eres un traductor profesional. Nunca inventes contenido. "
                            "Tu tarea es traducir frases de forma natural y precisa. "
                            "Si una frase tiene un significado idiomático o cultural, debes dar la traducción contextualizada correcta, "
                            "y no una traducción literal. Si no entiendes el significado, indica que la frase no se puede traducir de forma confiable."
                        )},
                        {"role": "user", "content": prompt_usuario}
                    ]
                )

                contenido = respuesta.choices[0].message.content.strip()
                if "\n" in contenido:
                    partes = contenido.split("\n", 1)
                    st.session_state.traduccion = partes[0].strip('"')
                    st.session_state.ejemplo = partes[1].strip()
                else:
                    st.session_state.traduccion = contenido.strip('"')
                    st.session_state.ejemplo = ""

            except Exception as e:
                st.error(f"❌ Error al traducir: {e}")

    # === Mostrar resultados ===
    if st.session_state.traduccion:
        st.success("Traducción contextualizada:")
        st.markdown(f"**{st.session_state.traduccion}**")

        cols = st.columns(3)
        with cols[0]:
            if st.button("🔊 Escuchar frase original"):
                reproducir_pronunciacion(
                    st.session_state.frase_original,
                    "es" if direccion.startswith("Español") else codigo_idioma
                )
        with cols[1]:
            if st.button("🔊 Escuchar traducción"):
                reproducir_pronunciacion(
                    st.session_state.traduccion,
                    codigo_idioma if direccion.startswith("Español") else "es"
                )
        with cols[2]:
            if st.session_state.ejemplo and st.button("🔊 Escuchar ejemplo"):
                reproducir_pronunciacion(
                    st.session_state.ejemplo,
                    codigo_idioma
                )

        if st.session_state.ejemplo:
            idioma_ejemplo = "es" if direccion.startswith("Español") else codigo_idioma
            etiqueta = "Español" if idioma_ejemplo == "es" else idioma.capitalize()
            st.markdown(f"💬 *Ejemplo en {etiqueta}:* {st.session_state.ejemplo}")


if __name__ == "__main__":
    traduccion_menu()