# utils/image_filter.py
from PIL import Image, ImageEnhance, ImageFilter as PILImageFilter
from collections import Counter

class ImageFilter:
    """
    Clase para aplicar filtros a las imágenes antes de guardarlas.
    """
    @staticmethod
    def apply_high_pass_filter_with_edges(image_path: str, output_path: str, brightness_factor: float = 3.0) -> str:
        """
        Aplica un filtro pasa-altas para intensificar los colores, detecta bordes
        y aumenta la iluminación, manteniendo el color original.

        :param image_path: Ruta de la imagen original.
        :param output_path: Ruta donde se guardará la imagen con el filtro aplicado.
        :param brightness_factor: Factor para ajustar la iluminación (1.0 = sin cambio).
        :return: Ruta de la imagen procesada.
        """
        try:
            # Abrir la imagen
            img = Image.open(image_path)

            # Paso 1: Incrementar saturación y contraste en la imagen original
            enhancer = ImageEnhance.Color(img)
            img_color = enhancer.enhance(4.0)  # Ajustar saturación
            contrast = ImageEnhance.Contrast(img_color)
            img_color_enhanced = contrast.enhance(2.0)  # Ajustar contraste

            # Paso 2: Aumentar la iluminación de la imagen
            brightness_enhancer = ImageEnhance.Brightness(img_color_enhanced)
            img_brightened = brightness_enhancer.enhance(brightness_factor)  # Ajustar iluminación

            # Paso 3: Convertir a escala de grises para detectar bordes
            img_gray = img_brightened.convert("L")

            # Definir un kernel para detectar bordes
            edge_kernel = PILImageFilter.Kernel(
                size=(3, 3),
                kernel=[
                    -1, -1, -1,
                    -1,  8, -1,
                    -1, -1, -1
                ],
                scale=1
            )

            # Aplicar el filtro para detectar bordes
            edges = img_gray.filter(edge_kernel)

            # Paso 4: Combinar bordes detectados con la imagen original
            edges_colored = edges.convert("RGB")  # Convertir bordes a RGB
            img_combined = Image.blend(img_brightened, edges_colored, alpha=0.5)  # Mezclar

            # Guardar la imagen procesada
            img_combined.save(output_path)

            return output_path
        except Exception as e:
            raise ValueError(f"Error al procesar la imagen: {str(e)}")

    @staticmethod
    def process_image(image_path: str, output_path: str) -> str:
        """
        Detecta bordes, conserva el color dominante y convierte el resto en negro.

        :param image_path: Ruta de la imagen original.
        :param output_path: Ruta donde se guardará la imagen procesada.
        :return: Ruta de la imagen procesada.
        """
        try:
            # Abrir la imagen original
            img = Image.open(image_path)
            img = img.convert("RGB")  # Asegurar que esté en RGB

            # Guardar la imagen procesada
            img.save(output_path)

            return output_path
        except Exception as e:
            raise ValueError(f"Error al procesar la imagen: {str(e)}")
    
    @staticmethod
    def pixelate_image(image_path: str, output_path: str, pixel_size: int) -> str:
        """
        Reduce la resolución de la imagen para pixelarla.

        :param image_path: Ruta de la imagen original.
        :param output_path: Ruta donde se guardará la imagen pixelada.
        :param pixel_size: Tamaño del bloque de píxeles.
        :return: Ruta de la imagen pixelada.
        """
        try:
            # Abrir la imagen
            img = Image.open(image_path)

            # Obtener las dimensiones originales
            original_size = img.size

            # Reducir la resolución
            img_small = img.resize(
                (original_size[0] // pixel_size, original_size[1] // pixel_size),
                Image.NEAREST
            )

            # Escalar de vuelta al tamaño original
            img_pixelated = img_small.resize(original_size, Image.NEAREST)

            # Guardar la imagen pixelada
            img_pixelated.save(output_path)

            return output_path
        except Exception as e:
            raise ValueError(f"Error al pixelar la imagen: {str(e)}")