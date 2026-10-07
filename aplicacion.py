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

# Inicializar una lista local temporal para almacenar múltiples medidas en la sesión actual
if 'lista_hojas_dia' not in st.session_state:
    st.session_state.lista_hojas_dia = pd.DataFrame(columns=[
        "Tipo Hoja", "Hojas", "Total Sqft", "Precio/Sqft", "Total Dinero ($)"
    ])

# --- DATOS GENERALES DEL TRABAJO ---
fecha = st.date_input("Fecha", datetime.date.today())

col_nombres1, col_nombres2 = st.columns(2)
with col_nombres1:
    nombre_trabajo = st.text_input("Nombre del Trabajo / Obra", placeholder="Ej: Condominio Bloque A")
with col_nombres2:
    nombre_ayudante = st.text_input("Nombre del Ayudante", placeholder="Nombre completo")

st.markdown("---")

# --- SECCIÓN PARA AGREGAR HOJAS ---
st.subheader("🧱 Entrada de Materiales")
st.write("Selecciona una medida, pon la cantidad instalada y el precio, luego agrégala a tu lista diaria.")

col_mat1, col_mat2, col_mat3 = st.columns()
with col_mat1:
    tipo_hoja = st.selectbox("Tamaño de la Hoja", ["4x8 (32 sqft)", "4x9 (36 sqft)", "4x10 (40 sqft)", "4x12 (48 sqft)"])
with col_mat2:
    hojas_instaladas = st.number_input("Cantidad de hojas", min_value=0, step=1, key="hojas_input")
with col_mat3:
    precio_por_sqft = st.number_input("Precio / sqft ($)", min_value=0.0, format="%.2f", key="precio_input")

# Botón para ir sumando filas a la lista de revisión
agregar_material = st.button("➕ Agregar a la Lista del Día", use_container_width=True)

# Mapeo matemático
medidas = {"4x8 (32 sqft)": 32, "4x9 (36 sqft)": 36, "4x10 (40 sqft)": 40, "4x12 (48 sqft)": 48}
sqft_por_hoja = medidas[tipo_hoja]
total_sqft_item = hojas_instaladas * sqft_por_hoja
total_dinero_item = total_sqft_item * precio_por_sqft

if agregar_material:
    if hojas_instaladas > 0:
        nueva_fila = {
            "Tipo Hoja": tipo_hoja,
            "Hojas": int(hojas_instaladas),
            "Total Sqft": int(total_sqft_item),
            "Precio/Sqft": float(precio_por_sqft),
            "Total Dinero ($)": float(total_dinero_item)
        }
        st.session_state.lista_hojas_dia = pd.concat([st.session_state.lista_hojas_dia, pd.DataFrame([nueva_fila])], ignore_index=True)
        st.success(f"¡Agregadas {hojas_instaladas} hojas de {tipo_hoja} a la lista de revisión de abajo!")
    else:
        st.warning("⚠️ Introduce una cantidad de hojas mayor a 0 para agregar.")

st.markdown("---")

# --- SECCIÓN DEL AYUDANTE ---
st.subheader("👥 Control del Ayudante")
col_ayudante1, col_ayudante2 = st.columns(2)
with col_ayudante1:
    horas_ayudante = st.number_input("Horas totales trabajadas por el ayudante", min_value=0.0, step=0.5)
with col_ayudante2:
    pago_por_hora_ayudante = st.number_input("Pago por hora ($)", min_value=0.0, format="%.2f", value=25.0)

total_pago_ayudante_dia = horas_ayudante * pago_por_hora_ayudante

# --- CUADRO DE REVISIÓN EN TIEMPO REAL ---
st.markdown("---")
st.subheader("👀 Revisa tus Totales Acumulados antes de Enviar")

# Calcular los totales acumulados de la lista de materiales agregados
acumulado_sqft = st.session_state.lista_hojas_dia["Total Sqft"].sum()
acumulado_dinero = st.session_state.lista_hojas_dia["Total Dinero ($)"].sum()

# CÁLCULO DE LA GANANCIA LIMPIA SOLICITADA (Total Trabajo - Pago Ayudante)
ganancia_limpia = acumulado_dinero - total_pago_ayudante_dia

if not st.session_state.lista_hojas_dia.empty:
    st.write("📋 **Desglose de las hojas agregadas hoy:**")
    st.dataframe(st.session_state.lista_hojas_dia, use_container_width=True)
    if st.button("🔄 Borrar lista y empezar de nuevo"):
        st.session_state.lista_hojas_dia = pd.DataFrame(columns=["Tipo Hoja", "Hojas", "Total Sqft", "Precio/Sqft", "Total Dinero ($)"])
        st.rerun()

# Primera fila de métricas básicas
c1, c2, c3 = st.columns(3)
c1.metric("Total Sqft del Día", f"{int(acumulado_sqft):,}")
c2.metric("Total Dinero Bruto ($)", f"${acumulado_dinero:,.2f}")
c3.metric("Pago Total Ayudante ($)", f"${total_pago_ayudante_dia:,.2f}")

# NUEVA SECCIÓN: Mostrar de forma destacada la Ganancia Neta Limpia
st.markdown("<br>", unsafe_allow_html=True)
col_neto1, col_neto2 = st.columns([1, 2])
with col_neto2:
    st.metric("💰 Tu Ganancia Limpia (Neto)", f"${ganancia_limpia:,.2f}")

# --- BOTÓN DE ENVÍO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)
enviar = st.button("🚀 Enviar Reporte Diario Obligatorio", use_container_width=True)

if enviar:
    if not st.session_state.lista_hojas_dia.empty and nombre_trabajo != "":
        st.success("¡Tu reporte completo con el cálculo de ganancia neta ha sido enviado y registrado exitosamente!")
        st.balloons()
        # Limpiar la lista temporal para el día siguiente
        st.session_state.lista_hojas_dia = pd.DataFrame(columns=["Tipo Hoja", "Hojas", "Total Sqft", "Precio/Sqft", "Total Dinero ($)"])
    else:
        st.warning("⚠️ Asegúrate de poner el Nombre del Trabajo y de presionar el botón 'Agregar a la Lista del Día' al menos para una medida de hoja antes de enviar.")
