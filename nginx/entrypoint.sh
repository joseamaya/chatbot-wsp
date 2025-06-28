#!/bin/sh

# Esperar a que el servicio de la app esté disponible
until curl -s app:8000 > /dev/null; do
    echo "Esperando a que la aplicación esté disponible..."
    sleep 5
done

# Verificar si ya existen certificados
if [ ! -d "/etc/letsencrypt/live" ]; then
    # Obtener certificados SSL
    certbot --nginx \
            --non-interactive \
            --agree-tos \
            --email miguel.amaya99@gmail.com \
            --domains ec2-18-231-178-130.sa-east-1.compute.amazonaws.com \
            --redirect
fi

# Iniciar el cron para la renovación automática
echo "0 0 1 * * certbot renew --quiet" > /etc/crontabs/root
crond

# Iniciar Nginx en primer plano
nginx -g "daemon off;"
