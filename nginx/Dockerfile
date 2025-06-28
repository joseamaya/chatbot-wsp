FROM nginx:1.25-alpine

# Instalar certbot y sus dependencias
RUN apk add --no-cache certbot certbot-nginx

# Copiar la configuración de Nginx
COPY chatbot.conf /etc/nginx/conf.d/default.conf

# Copiar el script de inicio
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Comando para ejecutar el script de inicio
ENTRYPOINT ["/entrypoint.sh"]
