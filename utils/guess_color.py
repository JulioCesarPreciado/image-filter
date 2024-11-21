from PIL import Image
from collections import Counter

class GuessColor:
    """
    Clase para determinar el color predominante de una imagen.
    """
    @staticmethod
    def get_dominant_color(image_path: str) -> str:
        """
        Obtiene el color predominante de una imagen en formato hexadecimal.

        :param image_path: Ruta de la imagen.
        :return: Color predominante en formato hexadecimal (#RRGGBB).
        """
        try:
            # Abrir la imagen
            img = Image.open(image_path)
            img = img.convert("RGB")  # Asegurar que esté en formato RGB

            # Reducir la imagen para acelerar el procesamiento
            small_img = img.resize((50, 50))  # Reducir la resolución
            pixels = list(small_img.getdata())  # Obtener todos los píxeles

            # Contar la frecuencia de cada color
            counter = Counter(pixels)
            most_common_color = counter.most_common(1)[0][0]  # Color más común (R, G, B)

            # Convertir el color a formato hexadecimal
            hex_color = "#{:02x}{:02x}{:02x}".format(*most_common_color)
            return hex_color
        except Exception as e:
            raise ValueError(f"Error al calcular el color predominante: {str(e)}")