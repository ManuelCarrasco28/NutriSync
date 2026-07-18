# Imagen base ligera de Python
FROM python:3.12-slim

# Evita que Python genere archivos .pyc (.py bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python almacene la salida en buffer (logs en tiempo real)
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo los requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Expone el puerto 8000 para el servidor web
EXPOSE 8000

# Ejecuta el servidor de desarrollo al levantar el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
