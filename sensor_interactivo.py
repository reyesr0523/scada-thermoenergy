import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# 1. Conexión segura con Firebase
cred = credentials.Certificate("llave_lab.json.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lab-hvac-r-reyesthermoenergy-default-rtdb.firebaseio.com/'
})

# Nodo de transmisión en la nube
nodo_sensor = db.reference('laboratorio_automatizacion/sensor_1')

# 2. Construcción de la interfaz gráfica primero (para que Python la conozca)
ventana = tk.Tk()
ventana.title("REYES THERMOENERGY - Panel Simulación")
ventana.geometry("400x300")
ventana.resizable(False, False)

# Etiquetas de título
lbl_titulo = ttk.Label(ventana, text="CONTROL DE CÁMARA FRIGORÍFICA", font=("Arial", 12, "bold"))
lbl_titulo.pack(pady=15)

lbl_sub = ttk.Label(ventana, text="Mueve el control para cambiar la temperatura del sensor:")
lbl_sub.pack(pady=5)

# Pantallas de lectura digital en la ventana (las creamos antes para que la función las encuentre)
lbl_temp_actual = ttk.Label(ventana, text="4.5 °C", font=("Arial", 24, "bold"))
lbl_temp_actual.pack(pady=10)

lbl_estado_compresor = ttk.Label(ventana, text="COMPRESOR: ON", font=("Arial", 11, "bold"), foreground="green")
lbl_estado_compresor.pack(pady=10)


# 3. Función de transmisión (Ahora sí sabe qué son 'lbl_temp_actual' y 'lbl_estado_compresor')
def transmitir_datos(valor_temperatura):
    temp = round(float(valor_temperatura), 1)
    
    # Lógica industrial de Setpoint
    estado_compresor = "ON" if temp > 4.0 else "OFF"
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Actualizamos los textos visuales en la ventana de Windows
    lbl_temp_actual.config(text=f"{temp} °C")
    if estado_compresor == "ON":
        lbl_estado_compresor.config(text=f"COMPRESOR: {estado_compresor}", foreground="green")
    else:
        lbl_estado_compresor.config(text=f"COMPRESOR: {estado_compresor}", foreground="red")
    
    # Guardamos localmente en tu historial.txt
    with open("historial.txt", "a") as archivo:
        archivo.write(f"[{hora_actual}] Temp: {temp}°C | Compresor: {estado_compresor}\n")
    
    # Mandamos los datos a Firebase
    nodo_sensor.set({
        'temperatura': temp,
        'estado_compresor': estado_compresor,
        'ultima_actualizacion': hora_actual
    })
    print(f"[{hora_actual}] Enviado a la nube -> Temp: {temp}°C | Compresor: {estado_compresor}")


# 4. El control deslizante apunta a la función una vez que ya está declarada
control_temperatura = ttk.Scale(
    ventana, 
    from_=-5.0, 
    to=15.0, 
    orient="horizontal", 
    length=300, 
    command=transmitir_datos
)
control_temperatura.set(4.5) # Arranca en 4.5°C
control_temperatura.pack(pady=15)

print("=== Ventana de simulación activa. Interactúa con el control en tu pantalla ===")
ventana.mainloop()