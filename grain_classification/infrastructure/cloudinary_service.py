import cloudinary
import cloudinary.uploader
import cv2
import numpy as np
from io import BytesIO
from shared.infrastructure.persistence.database.repositories.settings import settings


class CloudinaryService:
    """
    Servicio para subir imágenes de granos a Cloudinary
    """

    def __init__(self):
        # Configurar Cloudinary con las credenciales
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    @staticmethod
    def upload_grain_image(grain_image: np.ndarray,
                           session_id: str,
                           grain_index: int) -> dict:
        """
        Sube la imagen de un grano a Cloudinary

        Args:
            grain_image: Imagen del grano en formato numpy array (OpenCV)
            session_id: ID de la sesión de clasificación
            grain_index: Índice del grano en la sesión

        Returns:
            dict con 'url' y 'public_id' de la imagen subida
        """
        try:
            # Convertir la imagen de BGR (OpenCV) a RGB
            rgb_image = cv2.cvtColor(grain_image, cv2.COLOR_BGR2RGB)

            # Codificar la imagen a formato JPEG en memoria
            is_success, buffer = cv2.imencode(".jpg", rgb_image)
            if not is_success:
                raise ValueError("No se pudo codificar la imagen")

            # Convertir a bytes
            image_bytes = BytesIO(buffer.tobytes())

            # Generar un public_id único
            public_id = f"grains/{session_id}/grain_{grain_index}"

            # Subir a Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_bytes,
                public_id=public_id,
                folder="coffee_grains",
                resource_type="image",
                overwrite=True,
                transformation=[
                    {'width': 500, 'height': 500, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )

            return {
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id']
            }

        except Exception as e:
            print(f"Error al subir imagen a Cloudinary: {e}")
            return {
                'url': None,
                'public_id': None,
                'error': str(e)
            }

    @staticmethod
    def delete_grain_image(public_id: str) -> bool:
        """
        Elimina una imagen de Cloudinary
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Error al eliminar imagen de Cloudinary: {e}")
            return False