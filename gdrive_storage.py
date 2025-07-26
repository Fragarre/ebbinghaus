import streamlit as st
import os
import io
import pandas as pd
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# === Configuración ===
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = 'memoryData'  # carpeta en Google Drive

# SERVICE_ACCOUNT_FILE = 'service_account.json'  # asegúrate de tenerlo en tu proyecto
# # === Autenticación ===
# credentials = service_account.Credentials.from_service_account_file(
# SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# drive_service = build('drive', 'v3', credentials=credentials)

# === Autenticación desde secrets.toml ===
# service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
# credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(info)

drive_service = build('drive', 'v3', credentials=credentials)

# Verificación rápida de autenticación:
about = drive_service.about().get(fields="user").execute()
print("Autenticado como:", about["user"]["emailAddress"])
service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
st.write("Email autenticado:", service_account_info["client_email"])


# service_account_info = dict(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
# credentials = service_account.Credentials.from_service_account_info(service_account_info)
# drive_service = build('drive', 'v3', credentials=credentials)
# === Funciones ===

def get_folder_id(folder_name):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = drive_service.files().list(q=query, spaces='drive').execute()
    folders = response.get('files', [])
    if folders:
        return folders[0]['id']
    raise FileNotFoundError(f"Carpeta '{folder_name}' no encontrada en Google Drive.")


def subir_csv(local_path, drive_filename=None):
    if not drive_filename.endswith(".csv"):
        drive_filename += ".csv"
    folder_id = get_folder_id(FOLDER_NAME)

    # Buscar si ya existe el archivo
    query = (
        f"name = '{drive_filename}' and '{folder_id}' in parents and "
        f"mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    )
    response = drive_service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])
    file_id = files[0]['id'] if files else None

    media = MediaIoBaseUpload(io.open(local_path, 'rb'), mimetype='text/csv')

    if file_id:
        # ✅ Si existe, actualiza el contenido
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # ✅ Si no existe, crea nuevo
        file_metadata = {
            'name': drive_filename,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        drive_service.files().create(body=file_metadata, media_body=media).execute()

def descargar_csv(drive_filename):
    folder_id = get_folder_id(FOLDER_NAME)
    query = (
        f"name = '{drive_filename}' and '{folder_id}' in parents "
        f"and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    )
    response = drive_service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])
    if not files:
        raise FileNotFoundError(f"Archivo '{drive_filename}' no encontrado en Google Drive.")

    file_id = files[0]['id']
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)

    return pd.read_csv(fh, encoding="utf-8")  # o encoding="ISO-8859-1"


def delete_if_exists(filename, folder_id):
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    response = drive_service.files().list(q=query, spaces='drive').execute()
    for f in response.get('files', []):
        drive_service.files().delete(fileId=f['id']).execute()

def listar_tareas_csv():
    """
    Lista los nombres de archivos .csv disponibles en la carpeta de Google Drive 'memoryData'.
    Devuelve una lista de nombres sin la extensión '.csv'.
    """
    folder_id = get_folder_id(FOLDER_NAME)
    query = (
        f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' "
        f"and trashed = false and name contains '.csv'"
    )
    response = drive_service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])
    return [f["name"].replace(".csv", "") for f in files if f["name"].endswith(".csv")]
