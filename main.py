from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks

# Modules
import modules.func_detection as detection
import modules.google_storage as google_storage

# Start FastAPI
app = FastAPI()

credenciales_json = './tokens/validacionbiometrica-2c6740b82cc4.json'
GCS_BUCKET_NAME = "imgvalidacion"

class ImageData(BaseModel):
    cedula_image: str
    faces_image: str
    cedula: str

# Welcome message 
@app.get("/")
async def home():
    return {
        "message": "Welcome to Face_Detection API",
        "author": "Jorge Arguello al3x_argu",
    }

@app.get("/upload/")
async def help():
    return {
        "message": "Bienvenido a API Face_Compare",
        "manual": {
            "method": "La API utiliza una petición POST con formato JSON",
            "format": {
                "cedula_image": "image_in_base64", 
                "faces_image": "image_in_base64",
                "cedula": "1601000000"
            }
        },
        "response format": {
            "distance": "Mientras más cercana a 0, más similares son los rostros",
            "faces": "True or False",
            "cedula": "True or False",
            "save_on_google > True": [
                "1601000000_cedula.jpg",
                "1601000000_faces.jpg"
            ],
            "save_on_google > False": "False"
        }
    }

# Endpoint para cargar y comparar imágenes en formato JSON
@app.post("/upload/")
async def create_upload_files(data: ImageData, background_tasks: BackgroundTasks):
    try:
        # Crear un ThreadPoolExecutor para ejecutar las tareas en hilos
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Definir una función para la comparación de imágenes en un hilo
            def compare_images():
                return detection.face_compare(
                    data.cedula_image, 
                    data.faces_image
                )

            # Definir una función para la comparación de cédulas en otro hilo
            def compare_cedulas():
                return detection.text_detection(
                    credenciales_json, 
                    data.cedula_image, 
                    data.cedula
                )

            # Ejecutar ambas funciones en hilos separados y obtener los resultados
            result_images = executor.submit(compare_images)
            result_cedulas = executor.submit(compare_cedulas)

            # Esperar a que ambos hilos terminen y obtener los resultados
            result_images = result_images.result()
            result_cedulas = result_cedulas.result()

        # Comprobar los resultados y continuar con la parte de guardar en Google
        if result_images["faces"] and result_cedulas:
            # Guardando las imágenes en el google cloud en un hilo único
            background_tasks.add_task(
                google_storage.save,
                data.cedula_image,
                data.faces_image,
                data.cedula,
                GCS_BUCKET_NAME
            )
            save_on_google = [
                f"{data.cedula}_cedula.jpg", 
                f"{data.cedula}_faces.jpg"
            ]
        else:
            save_on_google = False

        # Construir y retornar la respuesta final
        response = {
            "distance": result_images["distance"],
            "faces": result_images["faces"],
            "cedula": result_cedulas,
            "save_on_google": save_on_google  
        }

        return response

    except Exception as e:
        return {
            "error as ocurred": str(e)
        }