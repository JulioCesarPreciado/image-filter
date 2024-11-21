from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
import os
import uuid
from dotenv import load_dotenv
# Configuración para servir imágenes estáticamente
from fastapi.staticfiles import StaticFiles
# Utils
from utils.image_filter import ImageFilter
from utils.guess_color import GuessColor

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener credenciales desde el archivo .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Crear carpeta de almacenamiento si no existe
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Crear la aplicación FastAPI
app = FastAPI()

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Autenticación de usuario
def authenticate_user(username: str, password: str):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"username": username}
    return None

# Validar el token
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != ADMIN_USERNAME:  # Usar el token como nombre de usuario directamente
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o no autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": token}

# Endpoint para obtener el token
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}

# Endpoint para subir imágenes con protección OAuth2
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Endpoint para recibir una imagen, aplicar pixelación y un filtro pasa-altas,
    guardar la imagen procesada y calcular el color predominante.
    """
    try:
        # Validar que el archivo sea de tipo imagen
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo no es una imagen válida"
            )

        # Crear un nombre único para la imagen
        file_name = f"{uuid.uuid4()}.jpg"
        temp_path = os.path.join(STORAGE_DIR, f"temp_{file_name}")
        pixelated_path = os.path.join(STORAGE_DIR, f"pixelated_{file_name}")
        edges_path = os.path.join(STORAGE_DIR, f"edges_{file_name}")
        final_path = os.path.join(STORAGE_DIR, file_name)

        # Guardar la imagen temporalmente
        with open(temp_path, "wb") as out_file:
            out_file.write(await file.read())

        # Paso 1: Aplicar pixelación
        pixel_size = 10  # Ajusta este valor según el nivel de pixelación deseado
        ImageFilter.pixelate_image(temp_path, pixelated_path, pixel_size)

        # Paso 2: Aplicar el filtro pasa-altas para intensificar colores y bordes
        ImageFilter.apply_high_pass_filter_with_edges(pixelated_path, edges_path)

        # Paso 3: Procesar bordes y conservar el color dominante
        ImageFilter.process_image(edges_path, final_path)

        # Calcular el color predominante
        dominant_color = GuessColor.get_dominant_color(final_path)

        # Eliminar los archivos temporales
        os.remove(temp_path)
        os.remove(pixelated_path)
        os.remove(edges_path)

        return {
            "status": "success",
            "message": f"Imagen procesada y guardada correctamente en '{final_path}'",
            "file_name": file_name,
            "dominant_color": dominant_color
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar la imagen: {str(e)}"
        )

    
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Genera un carrete de imágenes desde el directorio 'storage'."""
    try:
        # Obtener todos los archivos en el directorio
        files = os.listdir(STORAGE_DIR)
        image_files = [f for f in files if f.endswith((".jpg", ".jpeg", ".png"))]

        # Construir el HTML con las imágenes
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ampolludo</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }
                img { max-width: 300px; margin: 10px; border: 2px solid #ddd; border-radius: 5px; }
                .container { display: flex; flex-wrap: wrap; justify-content: center; }
            </style>
        </head>
        <body>
            <h1>Así veo yo</h1>
            <div class="container">
        """
        for image in image_files:
            image_url = f"/storage/{image}"  # Asumimos que las imágenes serán servidas estáticamente
            html += f'<img src="{image_url}" alt="{image}" />'

        html += """
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la página: {str(e)}")

app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")
