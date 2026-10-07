import streamlit as st
import pandas as pd
import datetime
import os

# Configuración corporativa de la página
st.set_page_config(page_title="Sanzza Company - Control de Drywall", page_icon="🏗️", layout="centered")

# --- LOGO Y NOMBRE DE LA COMPAÑÍA ---
# Si subiste el logo a tu repositorio como 'logo.png', se cargará automáticamente
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("Sistema de Control de Instalaciones")
st.subheader("Sanzza Company UX")
st.write("Portal de registro diario para instaladores y ayudantes de drywall.")

# Inicializar base de datos temporal (Se reemplazará con Google Sheets en la Parte 2)
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Fecha", "Trabajo / Obra", "Ayudante", "Tipo Hoja", "Hojas", "Total Sqft", "Precio/Sqft", "Total Dinero ($)", "Horas Ayudante", "Precio/Hora ($)", "Pago Ayudante ($)"
    ])

# --- FORMULARIO DE CAPTURA ---
st.header("📝 Registro del Día")

with st.form("registro_diario", clear_on_submit=False):
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
        "Fecha": fecha.strftime("%Y-%m-%d"), "Trabajo / Obra": nombre_trabajo, "Ayudante": nombre_ayudante,
        "Tipo Hoja": tipo_hoja, "Hojas": hojas_instaladas, "Total Sqft": total_sqft_dia, 
        "Precio/Sqft": precio_por_sqft, "Total Dinero ($)": total_dinero_dia, 
        "Horas Ayudante": horas_ayudante, "Precio/Hora ($)": pago_por_hora_ayudante, "Pago Ayudante ($)": total_pago_ayudante_dia
    }
    st.session_state.datos = pd.concat([st.session_state.datos, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("¡Tu reporte ha sido enviado y registrado exitosamente!")

# --- VISTA DE CONTROL EXCLUSIVA PARA EL ADMINISTRADOR ---
# Nota: Tus trabajadores verán la lista de abajo, pero tú la controlarás en Google Sheets de forma permanente.
if not st.session_state.datos.empty:
    st.header("📊 Historial General de Envíos")
    
    datos_editados = st.data_editor(st.session_state.datos, num_rows="dynamic", use_container_width=True)
    
    if not datos_editados.equals(st.session_state.datos):
        for idx, row in datos_editados.iterrows():
            try:
                hojas = int(row["Hojas"])
                tipo = row["Tipo Hoja"]
                p_sqft = float(row["Precio/Sqft"])
                hrs = float(row["Horas Ayudante"])
                p_hora = float(row["Precio/Hora ($)"])
                
                sqft_h = 32
                for k, v in medidas.items():
                    if k in str(tipo): sqft_h = v; break
                
                datos_editados.at[idx, "Total Sqft"] = hojas * sqft_h
                datos_editados.at[idx, "Total Dinero ($)"] = hojas * sqft_h * p_sqft
                datos_editados.at[idx, "Pago Ayudante ($)"] = hrs * p_hora
            except: pass
        st.session_state.datos = datos_editados
        st.rerun()

    acumulado_sqft = st.session_state.datos["Total Sqft"].sum()
    acumulado_dinero = st.session_state.datos["Total Dinero ($)"].sum()
    acumulado_horas = st.session_state.datos["Horas Ayudante"].sum()
    acumulado_pago_ayudante = st.session_state.datos["Pago Ayudante ($)"].sum()
    ganancia_neta = acumulado_dinero - acumulado_pago_ayudante
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sqft", f"{acumulado_sqft:,}")
    m2.metric("Total Bruto", f"${acumulado_dinero:,.2f}")
    m3.metric("Horas Ayudante", f"{acumulado_horas} hrs")
    
    m4, m5 = st.columns(2)
    m4.metric("Total Pagos Ayudantes", f"${acumulado_pago_ayudante:,.2f}", delta_color="inverse")
    m5.metric("Ganancia Limpia Sanzza", f"${ganancia_neta:,.2f}")
