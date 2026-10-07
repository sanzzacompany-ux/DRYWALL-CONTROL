import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_gsheets import GSheetsConnection

# Configuración corporativa de la página
st.set_page_config(page_title="Sanzza Company - Control de Drywall", page_icon="🏗️", layout="centered")

# --- LOGO Y NOMBRE DE LA COMPAÑÍA ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=180)

st.title("Sistema de Control de Instalaciones")
st.subheader("Sanzza Company UX")
st.write("Portal de registro diario para instaladores y ayudantes de drywall.")

# --- CONEXIÓN DIRECTA CON GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(ttl="5m")
except Exception as e:
    st.error("Error al conectar con la base de datos de Google. Asegúrate de configurar las llaves en los Secrets.")
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
    nuevo_registro = pd.DataFrame([{
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
    }])
    
    # Unir datos existentes con el nuevo reporte diario
    if not df_existente.empty:
        df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
    else:
        df_final = nuevo_registro
        
    # Guardar directamente en Google Sheets en la nube
    try:
        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_final)
        st.success("¡Tu reporte ha sido enviado y registrado exitosamente en la base de datos principal!")
        st.rerun()
    except Exception as e:
        st.error(f"Error al enviar datos: {e}")

# --- VISTA DE CONTROL DEL HISTORIAL ---
if df_existente is not None and not df_existente.empty:
    st.header("📊 Historial General de Envíos")
    st.dataframe(df_existente, use_container_width=True)
    
    acumulado_sqft = pd.to_numeric(df_existente["Total Sqft"]).sum()
    acumulado_dinero = pd.to_numeric(df_existente["Total Dinero ($)"]).sum()
    acumulado_horas = pd.to_numeric(df_existente["Horas Ayudante"]).sum()
    acumulado_pago_ayudante = pd.to_numeric(df_existente["Pago Ayudante ($)"]).sum()
    ganancia_neta = acumulado_dinero - acumulado_pago_ayudante
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sqft", f"{acumulado_sqft:,}")
    m2.metric("Total Bruto", f"${acumulado_dinero:,.2f}")
    m3.metric("Horas Ayudante", f"{acumulado_horas} hrs")
    
    m4, m5 = st.columns(2)
    m4.metric("Total Pagos Ayudantes", f"${acumulado_pago_ayudante:,.2f}", delta_color="inverse")
    m5.metric("Ganancia Limpia Sanzza", f"${ganancia_neta:,.2f}")
