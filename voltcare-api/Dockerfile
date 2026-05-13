# Imagen base con Go
FROM golang:1.26

# Instalar Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Crear directorio de trabajo
WORKDIR /app

# Copiar TODO el proyecto
COPY . .

# Instalar dependencias Python
RUN pip3 install -r requirements.txt --break-system-packages

# Entrar al backend Go
WORKDIR /app/voltcare-api

# Descargar dependencias Go
RUN go mod download

# Exponer puerto
EXPOSE 8080

# Ejecutar API
CMD ["go", "run", "cmd/main.go"]