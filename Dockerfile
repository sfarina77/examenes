# Usamos una imagen ligera oficial de Python
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc y fuerza el búfer de salida
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY admin_panel.py .

# Expone el puerto estándar que usa Cloud Run (8080)
EXPOSE 8080

# Comando para arrancar Streamlit configurado para escuchar en el puerto de GCP
CMD ["streamlit", "run", "admin_panel.py", "--server.port=8080", "--server.address=0.0.0.0"]