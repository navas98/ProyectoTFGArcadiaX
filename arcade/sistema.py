import hid
import time
import subprocess
import psutil
import os

# Configuración
VENDOR_ID = 0x0079
PRODUCT_ID = 0x0006
TIEMPO_LARGO = 5            # Tiempo necesario de pulsación para activar RetroBat (segundos)
INACTIVIDAD_MAX = 30        # Tiempo sin interacción para cerrar RetroBat (segundos)
RETROBAT_PATH = r"C:\retrobat\retrobat.exe"  # Ajusta la ruta si es diferente

retrobat_process = None
ultima_actividad = time.time()

# Función para cerrar todos los procesos relacionados con RetroBat
def cerrar_retrobat_completo():
    procesos_retrobat = [
        "retrobat.exe", "emulationstation.exe", "retroarch.exe", "pcsx2.exe",
        "mame.exe", "dolphin.exe", "snes9x.exe", "project64.exe", "citra.exe"
    ]
    cerrados = 0
    for proc in psutil.process_iter(['pid', 'name']):
        nombre = proc.info['name']
        if nombre and any(nombre.lower() == p for p in procesos_retrobat):
            try:
                print(f"🛑 Cerrando proceso: {nombre} (PID {proc.pid})")
                proc.terminate()
                proc.wait(timeout=5)
                cerrados += 1
            except Exception as e:
                print(f"⚠️ No se pudo cerrar {nombre}: {e}")
    if cerrados == 0:
        print("ℹ️ No se encontró ningún proceso de RetroBat.")

# Función para cerrar VLC si está en ejecución
def cerrar_vlc_si_abierto():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and "vlc.exe" in proc.info['name'].lower():
            try:
                proc.kill()
                print("🎵 VLC cerrado automáticamente.")
            except Exception as e:
                print(f"⚠️ No se pudo cerrar VLC: {e}")

def main():
    global retrobat_process, ultima_actividad

    # Abrimos el dispositivo HID
    dev = hid.device()
    dev.open(VENDOR_ID, PRODUCT_ID)
    dev.set_nonblocking(1)
    print("🎮 Botón arcade conectado.")

    pulsado = False
    inicio_pulsacion = None
    accion_realizada = False

    while True:
        data = dev.read(64)

        if data:
            boton_presionado = data[5] != 0  # Ajusta si otro byte representa el botón

            if boton_presionado:
                if not pulsado:
                    inicio_pulsacion = time.time()
                    pulsado = True
                    accion_realizada = False
                elif not accion_realizada and (time.time() - inicio_pulsacion) >= TIEMPO_LARGO:
                    print("🟢 Lanzando RetroBat...")
                    cerrar_vlc_si_abierto()  # Asegúrate de cerrarlo antes
                    retrobat_process = subprocess.Popen([RETROBAT_PATH], shell=True)
                    accion_realizada = True
                    ultima_actividad = time.time()
            else:
                pulsado = False
                inicio_pulsacion = None
                accion_realizada = False

            ultima_actividad = time.time()

        # Monitorear VLC mientras RetroBat está activo
        if retrobat_process and retrobat_process.poll() is None:
            cerrar_vlc_si_abierto()

        # Cierre por inactividad
        if time.time() - ultima_actividad >= INACTIVIDAD_MAX:
            print("⏳ Inactividad detectada. Cerrando RetroBat...")
            cerrar_retrobat_completo()
            retrobat_process = None
            ultima_actividad = time.time()

        time.sleep(0.05)

if __name__ == "__main__":
    main()
