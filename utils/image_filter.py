# utils/image_filter.py
from PIL import Image, ImageEnhance, ImageFilter as PILImageFilter

class ImageFilter:
    """
    Clase para aplicar filtros a las imágenes antes de guardarlas.
    """
    @staticmethod
    def apply_high_pass_filter(image_path: str, output_path: str) -> str:
        """
        Aplica un filtro pasa-altas para intensificar los colores de la imagen.

        :param image_path: Ruta de la imagen original.
        :param output_path: Ruta donde se guardará la imagen con el filtro aplicado.
        :return: Ruta de la imagen procesada.
        """
        try:
            # Abrir la imagen
            img = Image.open(image_path)

            # Aplicar un filtro pasa-altas
            detail_enhance = img.filter(PILImageFilter.DETAIL)

            # Incrementar saturación y contraste
            enhancer = ImageEnhance.Color(detail_enhance)
            img_color = enhancer.enhance(2.0)  # Ajustar saturación
            contrast = ImageEnhance.Contrast(img_color)
            img_final = contrast.enhance(1.0)  # Ajustar contraste

            # Guardar la imagen procesada
            img_final.save(output_path)

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