# 🧠 Aplicación de Memorización basada en la Curva del Olvido de Ebbinghaus

Esta aplicación ayuda a estudiantes y autodidactas a memorizar vocabulario, frases y expresiones en distintos idiomas mediante técnicas de **revisión espaciada**, inspiradas en la **curva del olvido de Ebbinghaus**.

## 🎯 Objetivos del proyecto

- Facilitar la memorización efectiva de contenidos lingüísticos.
- Clasificar ítems por dificultad y adaptar los tiempos de repaso en función del rendimiento del usuario.
- Integrar funcionalidades de traducción y generación de ejercicios con corrección automática.
- Ofrecer una experiencia intuitiva y multiplataforma a través de **Streamlit**.

## 🧩 Módulos principales

- **📋 Gestión**: Crear y mantener listas de estudio clasificadas por dificultad (`fácil`, `difícil`, `muy difícil`). Las listas se almacenan como archivos `.csv` en Google Drive.
- **⏳ Repaso**: Revisión diaria de ítems pendientes. Si el usuario recuerda, se alarga el plazo de revisión; si no, aumenta la dificultad.
- **🧪 Ejercicios**: Generación automática de frases en distintos idiomas con corrección automática de traducciones del usuario.
- **🌍 Traducción**: Traducción contextualizada con ejemplos reales en el idioma de destino. Incluye función de pronunciación por voz.

## 🌐 Idiomas compatibles

- Inglés  
- Francés  
- Italiano  
- Alemán  
- Portugués  

## ☁️ Almacenamiento

Los datos se guardan en una carpeta de Google Drive (`memoryData`) usando autenticación con `service_account.json`.

## 🤖 Inteligencia Artificial

Se utiliza la API de **OpenAI** (`gpt-4`) para:
- Generar ejercicios adaptados al idioma y nivel.
- Producir traducciones contextuales con ejemplos reales.

## 🔊 Pronunciación

Las frases pueden reproducirse en voz alta mediante la librería `gTTS`.

---

