import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Configurar MongoDB Atlas
client = AsyncIOMotorClient("mongodb+srv://javier:javier@cluster0.t5cgbal.mongodb.net/?retryWrites=true&w=majority")
db = client["arcadedatabe"]
collection = db["arcade"]

# Extensiones válidas
EXTENSIONES_ROM = [".nds"]
EXTENSIONES_IMAGEN = [".jpg", ".png", ".jpeg"]
EXTENSIONES_TRAILER = [".mp4"]

# Carpeta base
BASE_PATH = "C:/RetroBat/roms"

def normalizar_nombre(nombre_archivo):
    return os.path.splitext(nombre_archivo)[0].replace("_", " ").strip()

async def subir_juegos_por_carpeta():
    for consola in os.listdir(BASE_PATH):
        ruta_consola = os.path.join(BASE_PATH, consola)
        if not os.path.isdir(ruta_consola):
            continue

        for juego in os.listdir(ruta_consola):
            ruta_juego = os.path.join(ruta_consola, juego)
            if not os.path.isdir(ruta_juego):
                continue

            rom = imagen = trailer = None
            for archivo in os.listdir(ruta_juego):
                ruta_archivo = os.path.join(ruta_juego, archivo)
                ext = os.path.splitext(archivo)[1].lower()

                if ext in EXTENSIONES_ROM and not rom:
                    rom = ruta_archivo
                elif ext in EXTENSIONES_IMAGEN and not imagen:
                    imagen = ruta_archivo
                elif ext in EXTENSIONES_TRAILER and not trailer:
                    trailer = ruta_archivo

            if not rom:
                print(f"❌ No se encontró ROM en: {ruta_juego}")
                continue

            nombre = normalizar_nombre(os.path.basename(rom))

            # Verificar si ya existe
            existe = await collection.find_one({"nombre": nombre, "consola": consola})
            if existe:
                print(f"🔁 Ya existe: {nombre} ({consola})")
                continue

            doc = {
                "nombre": nombre,
                "ubicacion": rom,
                "consola": consola,
                "imagen": imagen,
                "trailer": trailer,
                "abierto": False,
                "play": False,
                "reproduciendo": False
            }

            await collection.insert_one(doc)
            print(f"✅ Insertado: {nombre} ({consola})")

# Ejecutar
if __name__ == "__main__":
    asyncio.run(subir_juegos_por_carpeta())
