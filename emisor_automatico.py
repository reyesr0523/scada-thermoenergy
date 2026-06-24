import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time
import random

# 1. Conexión segura con Firebase
cred = credentials.Certificate("llave_lab.json.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lab-hvac-r-reyesthermoenergy-default-rtdb.firebaseio.com/'
})

# Nodo de transmisión en la nube
nodo_sensor = db.reference('laboratorio_automatizacion/sensor_1')

# Variables iniciales de simulación térmica
temperatura_camara = 4.2  # Temperatura inicial en °C
estado_compresor = "OFF"
setpoint_alto = 5.0       # Temperatura de arranque del compresor
setpoint_bajo = 2.0       # Temperatura de parada (corte por frío)

print("=== SIMULADOR DE CICLO TERMODINÁMICO AUTOMÁTICO ACTIVO ===")
print("Transmitiendo datos de cámara frigorífica a Firebase de REYES THERMOENERGY...\n")

try:
    while True:
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Lógica de histéresis industrial (Control ON/OFF)
        if temperatura_camara >= setpoint_alto:
            estado_compresor = "ON"
        elif temperatura_camara <= setpoint_bajo:
            estado_compresor = "OFF"
            
        # Simulación del comportamiento físico de los fluidos y transferencia de calor
        if estado_compresor == "ON":
            # El compresor extrae calor: la temperatura baja dinámicamente con una pequeña variación de carga
            temperatura_camara -= round(random.uniform(0.15, 0.3), 1)
        else:
            # El compresor está apagado: la cámara gana calor del exterior por aislamiento/infiltración
            temperatura_camara += round(random.uniform(0.1, 0.2), 1)
            
        # Redondeo de precisión técnica a un decimal
        temperatura_camara = round(temperatura_camara, 1)
        
        # Guardamos localmente en tu registro de seguridad
        with open("historial.txt", "a") as archivo:
            archivo.write(f"[{hora_actual}] Temp: {temperatura_camara}°C | Compresor: {estado_compresor} (Auto)\n")
        
        # ¡Transmitimos el paquete IoT a tu base de datos de Firebase!
        nodo_sensor.set({
            'temperatura': temperatura_camara,
            'estado_compresor': estado_compresor,
            'ultima_actualizacion': hora_actual
        })
        
        print(f"[{hora_actual}] Transmitiendo -> Temp: {temperatura_camara}°C | Compresor: {estado_compresor}")
        
        # Frecuencia de envío del bus de datos (Cada 3 segundos para ver las curvas rápido)
        time.sleep(3)

except KeyboardInterrupt:
    print("\n=== Simulador automático detenido de forma segura ===")