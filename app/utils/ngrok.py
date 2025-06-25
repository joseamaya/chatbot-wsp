import os
from pyngrok import ngrok, conf


def setup_ngrok():
    """
    Configura y inicia un túnel ngrok para el servidor.

    Returns:
        str: La URL pública del túnel ngrok
    """
    ngrok_token = os.environ.get('NGROK_TOKEN')
    conf.get_default().auth_token = ngrok_token
    ngrok_tunel = ngrok.connect("8000", bind_tls=True)
    server_url = ngrok_tunel.public_url
    return server_url
