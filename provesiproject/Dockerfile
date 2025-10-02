# ---- Fase 1: Base ----
# Usamos una imagen oficial de Python como nuestra base.
FROM python:3.9-slim-buster

# ---- Variables de Entorno ----
# Evita que Python guarde la salida en un buffer para ver los logs en tiempo real.
ENV PYTHONUNBUFFERED 1

# ---- Instalación de Dependencias ----
# Creamos un directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos SOLO el archivo de requerimientos primero.
# Docker guarda en caché este paso para acelerar futuras construcciones.
COPY requirements.txt .

# Instalamos todas las librerías de Python.
RUN pip install -r requirements.txt

# ---- Copia del Código Fuente ----
# Ahora sí, copiamos el resto del código de tu proyecto al contenedor.
COPY . .

# ---- Comando de Ejecución ----
# El comando que se ejecutará cuando el contenedor inicie.
# Inicia el servidor Gunicorn en el puerto 8000 y le dice
# dónde está la configuración de tu aplicación (provesiproject.wsgi).
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "provesiproject.wsgi:application"]