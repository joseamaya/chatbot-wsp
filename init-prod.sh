#!/bin/bash

# Crear directorios necesarios
mkdir -p certbot/conf certbot/www nginx/conf

# Copiar la configuración de nginx si no existe
if [ ! -f "nginx/conf/chatbot.conf" ]; then
    cp nginx/chatbot.conf nginx/conf/
fi

# Iniciar los contenedores
docker-compose -f docker-compose.prod.yml up -d --build
