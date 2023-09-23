import face_recognition
import argparse

# Python Modules
from io import BytesIO
from PIL import Image
import base64
import numpy as np 

def base64_to_numpy(image):
    # Transformamos de base64 a numpy array
    image_bytes = base64.b64decode(image)
    # Crear un objeto BytesIO a partir de los bytes
    image_io = BytesIO(image_bytes)
    # Abrir la imagen utilizando la biblioteca PIL (Pillow)
    image = Image.open(image_io)
    # Convertir la imagen a una matriz numpy
    image_array = np.array(image)
    return image_array

def face_compare(image1, image2):
    """
    Recibe código en Base64
    """
    imagen1 = base64_to_numpy(image1)
    imagen2 = base64_to_numpy(image2)

    # Codificar los rostros en ambas imágenes
    codificacion1 = face_recognition.face_encodings(imagen1)[0]  
    codificacion2 = face_recognition.face_encodings(imagen2)[0]

    # Calcular la distancia euclidiana entre las codificaciones
    distancia = face_recognition.face_distance([codificacion1], codificacion2)[0]

    # El valor de distancia es un valor entre 0 y 1, donde 0 indica una similitud perfecta
    # Puedes establecer un umbral para decidir si las imágenes son suficientemente similares
    umbral = 0.5

    if distancia < umbral:
        answer = True
    else:
        answer = False
    
    return {
        "distancia": distancia,
        "answer": answer
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comparar rostros en dos imágenes.")
    parser.add_argument("ruta_1", help="Ruta de la primera imagen.")
    parser.add_argument("ruta_2", help="Ruta de la segunda imagen.")
    args = parser.parse_args()

    face_compare(args.ruta_1, args.ruta_2)