import time
from datetime import datetime

while True:
    # 1. Rutas exactas de tus archivos
    ruta_sensor = "c:/Users/Reinaldo/OneDrive/Documentos/DOCUMENTOS REINALDO/aplicaciones/Lab_Automatizacion/sensor.txt"
    ruta_historial = "c:/Users/Reinaldo/OneDrive/Documentos/DOCUMENTOS REINALDO/aplicaciones/Lab_Automatizacion/historial.txt"
    
    # 2. Abrimos y leemos el sensor
    with open(ruta_sensor, "r") as archivo:
        linea = archivo.read()
    
    datos = linea.split(",")
    equipo = datos[0]
    temperatura = float(datos[1])
    
    # 3. Evaluamos el estado según la temperatura
    if temperatura > 25:
        estado = "ALERTA: Temperatura alta. Encendiendo extractor."
    elif temperatura < 20:
        estado = "ALERTA: Temperatura baja. Encendiendo calefacción."
    else:
        estado = "Temperatura optima. Sistema en espera."
        
    # 4. Capturamos la fecha y hora actual del sistema
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 5. Creamos la línea que se va a guardar en el reporte
    linea_log = f"[{hora_actual}] Equipo: {equipo} | Temp: {temperatura}°C | Estado: {estado}\n"
    
    # 6. Guardamos la línea en el historial usando el modo 'a' (Añadir)
    with open(ruta_historial, "a") as log_archivo:
        log_archivo.write(linea_log)
        
    # Mostramos en la pantalla de VS Code para control visual
    print(f"Registrado en Historial -> {linea_log.strip()}")
    print("-" * 50)
    
    time.sleep(4)  # Medición cada 4 segundos