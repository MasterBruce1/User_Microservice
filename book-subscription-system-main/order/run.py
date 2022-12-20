import uvicorn
from fastapi import FastAPI
app = FastAPI()
#import os
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

# OAuth settings
GOOGLE_CLIENT_ID = '825199395476-18br125tl2m65lnr54evfuhtlquaj8p5.apps.googleusercontent.com' or None
GOOGLE_CLIENT_SECRET = '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' or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.get('/')
def public():
    return {'result': 'This is a public endpoint.'}


if __name__ == '__main__':
    uvicorn.run(app, port=8000)