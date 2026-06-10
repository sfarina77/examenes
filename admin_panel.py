import streamlit as st
import requests
import json
import base64

# =========================================================================
# CONFIGURACIÓN DE LAS CREDENCIALES DE GITHUB
# =========================================================================
# Extraemos el token de forma segura (sin escribirlo en el código)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  
REPO_OWNER = "sfarina77"
REPO_NAME = "examenes"
FILE_PATH = "examenes.json"
# =========================================================================

URL_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

st.set_page_config(page_title="Control de Exámenes", page_icon="🔒", layout="centered")

st.title("🎛️ Panel de Control - Sistema de Exámenes")
st.markdown("Gestiona los códigos, URLs y PINs de salida en tiempo real.")
st.divider()

def descargar_json_github():
    res = requests.get(URL_API, headers=HEADERS)
    if res.status_code == 200:
        datos_api = res.json()
        contenido_b64 = datos_api["content"]
        json_decodificado = base64.b64decode(contenido_b64).decode('utf-8')
        return json.loads(json_decodificado), datos_api["sha"]
    else:
        st.error("No se pudo conectar con GitHub. Verifica tu Token o Repositorio.")
        return {}, None

def guardar_json_github(diccionario_actualizado, sha, mensaje_commit):
    json_str = json.dumps(diccionario_actualizado, indent=2)
    json_b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": mensaje_commit,
        "content": json_b64,
        "sha": sha
    }
    
    res = requests.put(URL_API, headers=HEADERS, json=payload)
    if res.status_code == 200:
        st.success(f"🚀 ¡Servidor actualizado con éxito!")
        return True
    else:
        st.error("Error al guardar los cambios en GitHub.")
        return False

db_examenes, sha_actual = descargar_json_github()

if db_examenes:
    st.markdown("### 📋 Exámenes Activos en la Plataforma")
    for codigo, info in list(db_examenes.items()):
        with st.expander(f"🔹 {codigo} - {info['nombre']}"):
            st.write(f"**URL de Evaluación:** {info['url']}")
            st.write(f"**PIN de Cierre Docente:** `{info['pin_salida']}`")
            
            if st.button(f"🗑️ Eliminar {codigo}", key=f"del_{codigo}"):
                del db_examenes[codigo]
                if guardar_json_github(db_examenes, sha_actual, f"Se eliminó el examen {codigo}"):
                    st.columns(1) # Forzar refresco
                    
    st.divider()

    st.markdown("### ➕ Agregar / ✏️ Modificar Examen")
    
    with st.form("formulario_examen", clear_on_submit=True):
        nuevo_codigo = st.text_input("Código del Examen (Ej: EXAM303)").strip().upper()
        nuevo_nombre = st.text_input("Nombre Descriptivo (Ej: Examen de Admisión)")
        nueva_url = st.text_input("URL de la Evaluación")
        nuevo_pin = st.text_input("PIN de Salida del Docente")
        
        enviar = st.form_submit_button("Guardar Cambios")
        
        if enviar:
            if not nuevo_codigo or not nuevo_nombre or not nueva_url or not nuevo_pin:
                st.warning("Por favor rellena todos los campos.")
            else:
                db_examenes[nuevo_codigo] = {
                    "nombre": nuevo_nombre,
                    "url": nueva_url,
                    "pin_salida": nuevo_pin
                }
                if guardar_json_github(db_examenes, sha_actual, f"Se actualizó/creó el examen {nuevo_codigo}"):
                    st.columns(1)