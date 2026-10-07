import streamlit as st
import pandas as pd
import datetime

# Configuración de la aplicación
st.set_page_config(page_title="Control de Drywall", page_icon="🏗️", layout="centered")

st.title("🏗️ Control Diario de Instalación de Drywall")
st.write("Registra el trabajo diario, calcula el total de sqft, dinero y horas/pago del ayudante.")

# --- FORMULARIO DE CAPTURA ---
st.header("📝 Registro del Día")

with st.form("registro_diario", clear_on_submit=True):
    fecha = st.date_input("Fecha", datetime.date.today())
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_hoja = st.selectbox("Tamaño de la Hoja", ["4x8 (32 sqft)", "4x9 (36 sqft)", "4x10 (40 sqft)", "4x12 (48 sqft)"])
        hojas_instaladas = st.number_input("Cantidad de hojas instaladas", min_value=0, step=1)
        precio_por_sqft = st.number_input("Precio de instalación por sqft ($)", min_value=0.0, format="%.2f")
    
    with col2:
        horas_ayudante = st.number_input("Horas trabajadas por el ayudante", min_value=0.0, step=0.5)
        pago_por_hora_ayudante = st.number_input("Pago por hora del ayudante ($)", min_value=0.0, format="%.2f", value=15.0)

    enviar = st.form_submit_button("Guardar Registro")

# Mapeo del tamaño de la hoja a sqft reales (Se agregó la de 9 pies)
medidas = {
    "4x8 (32 sqft)": 32, 
    "4x9 (36 sqft)": 36, 
    "4x10 (40 sqft)": 40, 
    "4x12 (48 sqft)": 48
}
sqft_por_hoja = medidas[tipo_hoja]
total_sqft_dia = hojas_instaladas * sqft_por_hoja
total_dinero_dia = total_sqft_dia * precio_por_sqft
total_pago_ayudante_dia = horas_ayudante * pago_por_hora_ayudante

# Inicializar base de datos en la nube temporal de la página
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Fecha", "Tipo Hoja", "Hojas", "Total Sqft", "Precio/Sqft", "Total Dinero ($)", "Horas Ayudante", "Pago Ayudante ($)"
    ])

if enviar and hojas_instaladas > 0:
    nuevo_registro = {
        "Fecha": fecha, "Tipo Hoja": tipo_hoja, "Hojas": hojas_instaladas,
        "Total Sqft": total_sqft_dia, "Precio/Sqft": precio_por_sqft,
        "Total Dinero ($)": total_dinero_dia, "Horas Ayudante": horas_ayudante,
        "Pago Ayudante ($)": total_pago_ayudante_dia
    }
    st.session_state.datos = pd.concat([st.session_state.datos, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("¡Datos guardados correctamente!")

# --- VISTA DE RESULTADOS ---
if not st.session_state.datos.empty:
    st.header("📊 Resumen Acumulado Total")
    
    acumulado_sqft = st.session_state.datos["Total Sqft"].sum()
    acumulado_dinero = st.session_state.datos["Total Dinero ($)"].sum()
    acumulado_horas = st.session_state.datos["Horas Ayudante"].sum()
    acumulado_pago_ayudante = st.session_state.datos["Pago Ayudante ($)"].sum()
    ganancia_neta = acumulado_dinero - acumulado_pago_ayudante
    
    # Tarjetas de totales
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sqft", f"{acumulado_sqft:,}")
    m2.metric("Total Dinero Bruto", f"${acumulado_dinero:,.2f}")
    m3.metric("Horas Ayudante", f"{acumulado_horas} hrs")
    
    m4, m5 = st.columns(2)
    m4.metric("Total Pago Ayudante", f"${acumulado_pago_ayudante:,.2f}", delta_color="inverse")
    m5.metric("Tu Ganancia Limpia", f"${ganancia_neta:,.2f}")
    
    st.subheader("📋 Historial de Registros")
    st.dataframe(st.session_state.datos)
    
    csv = st.session_state.datos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte en Excel (CSV)",
        data=csv,
        file_name=f"reporte_drywall_{datetime.date.today()}.csv",
        mime='text/csv',
    )
else:
    st.info("Aún no hay registros guardados. Introduce los datos arriba para empezar.")
