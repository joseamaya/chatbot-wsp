import os


def setup_ngrok():
    from pyngrok import ngrok, conf
    ngrok_token = os.environ.get('NGROK_TOKEN')
    conf.get_default().auth_token = ngrok_token
    ngrok_tunel = ngrok.connect("8000", bind_tls=True)
    server_url = ngrok_tunel.public_url
    return server_url