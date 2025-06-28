#!/bin/sh

# Iniciar Nginx sin SSL primero
nginx

# Esperar a que el servicio de la app esté disponible
until curl -s app:8000 > /dev/null; do
    echo "Esperando a que la aplicación esté disponible..."
    sleep 5
done

# Obtener certificado SSL
certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email miguel.amaya99@gmail.com \
        --domains ec2-18-231-178-130.sa-east-1.compute.amazonaws.com \
        --redirect

# Configurar la renovación automática
echo "0 0 1 * * certbot renew --quiet" > /etc/crontabs/root
crond

# Recargar Nginx para aplicar la configuración SSL
nginx -s reload

# Mantener el contenedor ejecutándose
nginx -g "daemon off;"
