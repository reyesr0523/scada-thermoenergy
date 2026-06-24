import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time
import random

# 1. Cargamos tu llave digital segura
cred = credentials.Certificate("llave_lab.json.json")

# 2. Inicializamos la conexión con tu base de datos de REYES THERMOENERGY LAB
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lab-hvac-r-reyesthermoenergy-default-rtdb.firebaseio.com/'
})

print("=======================================================")
print("=== CONEXIÓN ACTIVA: REYES THERMOENERGY TELEMETRÍA ===")
print("=== Presiona Ctrl + C en la terminal para detener   ===")
print("=======================================================\n")

# 3. Ubicación del sensor en la nube
nodo_sensor = db.reference('laboratorio_automatizacion/sensor_1')

# Temperatura inicial de partida para la simulación
temperatura_actual = 4.5 

# 4. Bucle infinito para transmisión en tiempo real
try:
    while True:
        # Simulamos una pequeña variación térmica realista (-0.3°C a +0.3°C)
        variacion = random.uniform(-0.3, 0.3)
        temperatura_actual = round(temperatura_actual + variacion, 1)
        
        # Forzamos a que se mantenga en un rango lógico de refrigeración (0°C a 8°C)
        if temperatura_actual < 1.0: temperatura_actual = 1.5
        if temperatura_actual > 7.0: temperatura_actual = 6.0
        
        # Definimos el estado del compresor según la temperatura
        estado_compresor = "ON" if temperatura_actual > 4.0 else "OFF"
        
        hora_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Creamos el paquete de datos
        datos_sensor = {
            'temperatura': temperatura_actual,
            'estado_compresor': estado_compresor,
            'ultima_actualizacion': hora_envio
        }
        
        # Subimos los datos a Firebase
        nodo_sensor.set(datos_sensor)
        
        # Mostramos control visual en la consola de VS Code
        print(f"[{hora_envio}] Transmitiendo -> Temp: {temperatura_actual}°C | Compresor: {estado_compresor}")
        
        # Pausa de 5 segundos antes de la siguiente lectura
        time.sleep(5)

except KeyboardInterrupt:
    print("\n\n=== Simulador detenido de forma segura por el usuario ===")
except Exception as e:
    print(f"\nOcurrió un error en el envío: {e}")