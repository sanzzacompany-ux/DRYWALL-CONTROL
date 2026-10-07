import streamlit as st
import pandas as pd
import datetime
import os

# Configuración corporativa de la página
st.set_page_config(page_title="Sanzza Company - Control de Drywall", page_icon="🏗️", layout="centered")

# --- LOGO CENTRADO EN TAMAÑO GRANDE ---
col_logo1, col_logo2, col_logo3 = st.columns(3)
with col_logo2:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=350, use_container_width=True)
    elif os.path.exists("Logo.jpg"):
        st.image("Logo.jpg", width=350, use_container_width=True)

# TÍTULO PRINCIPAL
st.title("Sistema de Control de Drywall")
st.header("Registro del Día")

# --- FORMULARIO DE CAPTURA COMPLETO ---
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
    pago_por_hora_ayudante = st.number_input("Pago por hora ($)", min_value=0.0, format="%.2f", value=25.0)

# --- PROCESAMIENTO MATEMÁTICO EN TIEMPO REAL ---
medidas = {"4x8 (32 sqft)": 32, "4x9 (36 sqft)": 36, "4x10 (40 sqft)": 40, "4x12 (48 sqft)": 48}
sqft_por_hoja = medidas[tipo_hoja]
total_sqft_dia = hojas_instaladas * sqft_por_hoja
total_dinero_dia = total_sqft_dia * precio_por_sqft
total_pago_ayudante_dia = horas_ayudante * pago_por_hora_ayudante

# --- CUADRO DE REVISIÓN EN TIEMPO REAL (ANTES DE ENVIAR) ---
st.markdown("---")
st.subheader("👀 Revisa tus Totales antes de Enviar")
st.write("Verifica que los cálculos de abajo sean correctos. Si hay un error, cambia los números de arriba.")

c1, c2, c3 = st.columns(3)
c1.metric("Total Sqft a Reportar", f"{total_sqft_dia:,}")
c2.metric("Total Dinero Trabajo ($)", f"${total_dinero_dia:,.2f}")
c3.metric("Pago Total Ayudante ($)", f"${total_pago_ayudante_dia:,.2f}")

# --- BOTÓN DE ENVÍO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)
enviar = st.button("🚀 Enviar Reporte Diario Obligatorio", use_container_width=True)

if enviar:
    if hojas_instaladas > 0 and nombre_trabajo != "":
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
        
        # Confirmación visual de éxito
        st.success("¡Tu reporte ha sido enviado y registrado exitosamente!")
        st.balloons()
    else:
        st.warning("⚠️ Por favor introduce el Nombre del Trabajo y una cantidad válida de hojas antes de enviar.")
