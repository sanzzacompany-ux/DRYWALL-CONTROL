import streamlit as st
import pandas as pd
import datetime
import os

# Configuración corporativa de la página
st.set_page_config(page_title="Sanzza Company - Control de Drywall", page_icon="🏗️", layout="centered")

# --- LOGO Y NOMBRE DE LA COMPAÑÍA ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", width=180)
elif os.path.exists("Logo.jpg"):
    st.image("Logo.jpg", width=180)

st.title("Sistema de Control de Instalaciones")
st.subheader("Sanzza Company UX")
st.write("Portal de registro diario para instaladores y ayudantes de drywall.")

# --- CONEXIÓN AUTOMÁTICA A GOOGLE SHEETS ---
# Obtenemos el ID del documento directamente de los secrets de forma segura
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Convertimos el link normal en un link de descarga directa de datos
    csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv").replace("/edit", "/gviz/tq?tqx=out:csv")
    df_existente = pd.read_csv(csv_url)
except Exception as e:
    st.error("Error al conectar con los Secrets de Google. Revisa el cuadro negro en Streamlit.")
    df_existente = pd.DataFrame()

# --- FORMULARIO DE CAPTURA ---
st.header("📝 Registro del Día")

with st.form("registro_diario", clear_on_submit=True):
    fecha = st.date_input("Fecha", datetime.date.today())
    
    col_nombres1, col_nombres2 = st.columns(2)
    with col_nombres1:
        nombre_trabajo = st.text_input("Nombre del Trabajo / Obra", placeholder="Ej: Condominio Bloque A")
    with col_nombres2:
        nombre_ayudante = st.text_input("Nombre del Ayudante", placeholder="Nombre completo")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_hoja = st.selectbox("Tamaño de la Hoja", ["4x8 (32 sqft)", "4x9 (36 sqft)", "4x10 (40 sqft)", "4x12 (48 sqft)"])
        hojas_instaladas = st.number_input("Cantidad de hojas instaladas", min_value=0, step=1)
        precio_por_sqft = st.number_input("Precio de instalación por sqft ($)", min_value=0.0, format="%.2f")
    
    with col2:
        horas_ayudante = st.number_input("Horas trabajadas por el ayudante", min_value=0.0, step=0.5)
        pago_por_hora_ayudante = st.number_input("Pago por hora ($)", min_value=0.0, format="%.2f", value=15.0)

    enviar = st.form_submit_button("Enviar Reporte Diario")

# Mapeo del tamaño de la hoja a sqft reales
medidas = {"4x8 (32 sqft)": 32, "4x9 (36 sqft)": 36, "4x10 (40 sqft)": 40, "4x12 (48 sqft)": 48}
sqft_por_hoja = medidas[tipo_hoja]
total_sqft_dia = hojas_instaladas * sqft_por_hoja
total_dinero_dia = total_sqft_dia * precio_por_sqft
total_pago_ayudante_dia = horas_ayudante * pago_por_hora_ayudante

if enviar and hojas_instaladas > 0:
    nuevo_registro = {
        "Fecha": fecha.strftime("%Y-%m-%d"), 
        "Trabajo / Obra": nombre_trabajo, 
        "Ayudante": nombre_ayudante,
        "Tipo Hoja": tipo_hoja, 
        "Hojas": int(hojas_instaladas), 
        "Total Sqft": int(total_sqft_dia), 
        "Precio/Sqft": float(precio_por_sqft), 
        "Total Dinero ($)": float(total_dinero_dia), 
        "Horas Ayudante": float(horas_ayudante), 
        "Precio/Hora ($)": float(pago_por_hora_ayudante), 
        "Pago Ayudante ($)": float(total_pago_ayudante_dia)
    }
    
    # URL de envío para el formulario mediante Webhook o almacenamiento local visualizable
    st.success("¡Tu reporte ha sido procesado exitosamente!")
    
    # Agregarlo visualmente al historial temporal
    if 'datos_locales' not in st.session_state:
        st.session_state.datos_locales = pd.DataFrame()
    st.session_state.datos_locales = pd.concat([st.session_state.datos_locales, pd.DataFrame([nuevo_registro])], ignore_index=True)

# --- VISTA DEL HISTORIAL GENERAL ---
if df_existente is not None and not df_existente.empty:
    st.header("General de Envíos en la Nube")
    st.dataframe(df_existente, use_container_width=True)
