import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import time
from datetime import datetime
import os
from PIL import Image

# ==============================================================================
# 0. CONFIGURACIÓN DEL ENTORNO CORPORATIVO (NORMATIVAS E ISO)
# ==============================================================================
st.set_page_config(
    page_title="REYES THERMOENERGY | SCADA Eco-IoT", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# # Inicializar Firebase de forma segura (Adaptable para Local y Nube)
if not firebase_admin._apps:
    if os.path.exists("llave_lab.json.json"):
        # Si estás en tu PC, lee el archivo local
        cred = credentials.Certificate("llave_lab.json.json")
    else:
        # Si está en la nube de Streamlit, lee los secretos seguros incorporados
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://lab-hvac-r-reyesthermoenergy-default-rtdb.firebaseio.com/'
    })

# Conexión al nodo del sensor en Firebase
nodo_sensor = db.reference('laboratorio_automatizacion/sensor_1')

# Inicializar el historial de datos en la memoria de la sesión
if "historial_scada" not in st.session_state:
    st.session_state.historial_scada = pd.DataFrame(
        columns=["Fecha_Hora", "Temperatura_C", "Compresor", "Consumo_kW", "Emisiones_CO2"]
    )

# ==============================================================================
# 1. ENCABEZADO: INTEGRACIÓN DE TU LOGO CORPORATIVO REAL (BLINDADO)
# ==============================================================================
col_logo, col_titulo = st.columns([1, 2])

with col_logo:
    try:
        # Lista de posibles nombres y formatos que puede tener tu logo en el servidor
        posibles_logos = ["LOGO EMPRESA.jpeg", "LOGO EMPRESA.jpg", "LOGO EMPRESA.png"]
        logo_encontrado = None
        
        for nombre_archivo in posibles_logos:
            if os.path.exists(nombre_archivo):
                logo_encontrado = nombre_archivo
                break
        
        if logo_encontrado:
            imagen_logo = Image.open(logo_encontrado)
            st.image(imagen_logo, use_container_width=True)
        else:
            st.info("📌 Archivo de imagen 'LOGO EMPRESA' no detectado o incompatible.")
            
    except Exception as e:
        st.error(f"Error al procesar la imagen del logo: {e}")

with col_titulo:
    st.subheader("REYES THERMOENERGY E.I.R.L.")
    st.caption("Ingeniería de Fluidos, Termodinámica Cíclica y Sistemas de Energía Limpia")
    st.markdown("**Plataforma de Gestión Energética e Indicadores de Sostenibilidad**")

st.markdown("---")
# ==============================================================================
# 2. NUEVO SECTOR: CONFIGURACIÓN DEL REFRIGERANTE (COMPLIANCE AMBIENTAL)
# ==============================================================================
st.markdown("### 🎛️ Configuración de Fluido Refrigerante en Planta")

# Selector de gas industrial para auditorías ambientales externas
refrigerante_seleccionado = st.selectbox(
    "Selecciona el gas refrigerante cargado en el sistema cíclico:",
    ["R-744 (Dióxido de Carbono - Gas Natural)", "R-717 (Amoníaco - Cero Impacto)", "R-404A (HFC Comercial - Alto GWP)"],
    index=0
)

# Diccionario técnico de bases de datos ASHRAE (GWP = Global Warming Potential)
DATOS_REFRIGERANTES = {
    "R-744 (Dióxido de Carbono - Gas Natural)": {"GWP": 1, "Clase": "A1 (Seguro)", "Norma": "Sostenible / Eco-Friendly"},
    "R-717 (Amoníaco - Cero Impacto)": {"GWP": 0, "Clase": "B2L (Tóxico/Inflamable bajo)", "Norma": "Alta Eficiencia Industrial"},
    "R-404A (HFC Comercial - Alto GWP)": {"GWP": 3922, "Clase": "A1 (Seguro)", "Norma": "Fase de Retiro / Protocolo Montreal"}
}

gas_info = DATOS_REFRIGERANTES[refrigerante_seleccionado]
gwp_actual = gas_info["GWP"]

# Contenedores dinámicos para actualización en tiempo real (Dentro del bucle)
marcador_alerta = st.empty()
marcador_kpis_tecnicos = st.empty()
marcador_sustentabilidad = st.empty()
marcador_grafica = st.empty()
marcador_sincronizacion = st.empty()

# Elemento estático para la descarga (FUERA del bucle infinito para evitar duplicados)
st.markdown("### 📥 Reportes de Auditoría Ambiental")

def obtener_csv():
    return st.session_state.historial_scada.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Exportar Reporte Técnico e ISO (HACCP / ISO 14064)",
    data=obtener_csv(),
    file_name=f"Reyes_Thermoenergy_EcoSCADA_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True,
    key="boton_descarga_scada"
)

# ==============================================================================
# 3. BUCLE SCADA EN TIEMPO REAL CON CÁLCULOS TERMODINÁMICOS
# ==============================================================================
while True:
    datos = nodo_sensor.get()
    
    if datos:
        temp = datos.get('temperatura', 0.0)
        estado = datos.get('estado_compresor', 'UNKNOWN')
        actualizacion = datos.get('ultima_actualizacion', '---')
        
        # --- MODELADO Y CÁLCULOS DE INGENIERÍA ---
        if estado == "ON":
            consumo_kw = round(4.5 + (temp * 0.05), 2)  
        else:
            consumo_kw = 0.20  
            
        # Factor de emisión eléctrico base
        emisiones_co2 = round(consumo_kw * 0.202, 3)
        
        # COP Termodinámico estimado (ASHRAE / Carnot simplificado)
        if estado == "ON" and temp != 0:
            cop_estimado = round(abs(273.15 + temp) / abs(temp - 45.0), 2)
        else:
            cop_estimado = 0.0
            
        # --- GUARDAR HISTORIAL ---
        ahora_str = datetime.now().strftime("%H:%M:%S")
        if st.session_state.historial_scada.empty or st.session_state.historial_scada.iloc[-1]["Temperatura_C"] != temp:
            nueva_fila = pd.DataFrame([{
                "Fecha_Hora": ahora_str, 
                "Temperatura_C": temp, 
                "Compresor": estado,
                "Consumo_kW": consumo_kw,
                "Emisiones_CO2": emisiones_co2
            }])
            st.session_state.historial_scada = pd.concat([st.session_state.historial_scada, nueva_fila]).tail(30)

        # --- RE-RENDERIZAR MEDIDORES EN SUS MARCADORES ---
        with marcador_alerta.container():
            if temp > 10.0:
                st.error(f"⚠️ **DESVIACIÓN CRÍTICA DETECTADA** | Pérdida de Eficiencia Térmica. Temperatura: {temp} °C")
            else:
                st.success("✅ **SISTEMA EFICIENTE** | Operación bajo parámetros de Consumo Óptimo (HACCP & ISO 14001)")

        with marcador_kpis_tecnicos.container():
            st.markdown("### 📊 Monitoreo de Variables Técnicas (Ciclo Frigorífico)")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Temperatura Sensor 1", value=f"{temp} °C")
            col2.metric(label="Estado del Compresor", value=f"RUNNING ({estado})" if estado == "ON" else "STANDBY (OFF)")
            col3.metric(label="Eficiencia del Ciclo (COP)", value=f"{cop_estimado} Pts" if cop_estimado > 0 else "0.00 STR")

        with marcador_sustentabilidad.container():
            st.markdown("### 🌱 Indicadores Ambientales y Potencial de Gas (ISO 14064)")
            col_sust_1, col_sust_2, col_sust_3 = st.columns(3)
            
            col_sust_1.metric(label="Demanda Instantánea", value=f"{consumo_kw} kW")
            col_sust_2.metric(label="Huella de Carbono (Red)", value=f"{emisiones_co2} kg CO₂/h")
            
            # KPI Dinámico de Impacto por Fuga (GWP)
            if gwp_actual > 1000:
                col_sust_3.metric(label="Índice PCA / GWP (Fuga)", value=f"{gwp_actual}", delta="ALTO IMPACTO", delta_color="inverse")
            else:
                col_sust_3.metric(label="Índice PCA / GWP (Fuga)", value=f"{gwp_actual}", delta="ECO-EFICIENTE")
                
            st.caption(f"**Seguridad ASHRAE:** {gas_info['Clase']} | **Estatus Normativo:** {gas_info['Norma']}")
            st.markdown("---")

        with marcador_grafica.container():
            st.markdown("### 📈 Líneas de Tendencia del Sistema Integrado")
            if not st.session_state.historial_scada.empty:
                df_grafica = st.session_state.historial_scada.set_index("Fecha_Hora")
                st.line_chart(df_grafica[["Temperatura_C", "Consumo_kW"]])

        with marcador_sincronizacion.container():
            st.caption(f"Última lectura del bus de datos IoT: {actualizacion} | REYES THERMOENERGY E.I.R.L.")

    time.sleep(2)