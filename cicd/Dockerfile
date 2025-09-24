# Usa una imagen base liviana
FROM python:3.12-slim

# Evita prompts interactivos de APT
ENV DEBIAN_FRONTEND=noninteractive

# Establece directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar extensiones, incluyendo Rust
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    curl \
    pkg-config \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Rust (necesario para algunas librerías como pydantic_core y chromadb)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "$HOME/.cargo/env"

# Agrega Cargo al PATH para que esté disponible en los próximos pasos
ENV PATH="/root/.cargo/bin:${PATH}"

# Copia e instala dependencias sin cache
COPY cicd/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY /app/ /app

# Expone el puerto que usa Streamlit
EXPOSE 8501
