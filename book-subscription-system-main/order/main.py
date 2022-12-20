import json

from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Form
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from model import Order
import schema
from database import SessionLocal, engine
import model
from datetime import datetime
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

a = 12
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")
config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
model.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/orders")
async def read_orders(request: Request, db: Session = Depends(get_database_session)):
    orders = db.query(Order).all()
    html2 = (
        # f'<pre>{orders}</pre>'
        f'<a href="/logout">logout</a>'
    )
    return HTMLResponse(html2), orders


@app.post("/orderspost")
async def create_order(request: Request, db: Session = Depends(get_database_session)):
    global a
    data = await request.json()
    print(data)
    order = Order(user_id=data["user_id"], book_id=data["book_id"], book_name=data["book_name"], price=data["price"],
                  subcribed_at=datetime.now())
    db.add(order)
    db.commit()
    db.refresh(order)
    #response = RedirectResponse('/orders', status_code=303) #status_code=303
    response = RedirectResponse(url='/orders')
    return response


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            # f'<pre>{data}</pre>'
            f'<a href="/orderspost">please order your book~ </a><br/>'
            f'<a href="/orders">check your orders</a><br/>'
            f'<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
# @app.get("/", response_class=HTMLResponse)
# async def read_item(request: Request, db: Session = Depends(get_database_session)):
#     records = db.query(Order).all()
#     return templates.TemplateResponse("index.html", {"request": request, "data": records})
#
#
# @app.get("/movie/{name}", response_class=HTMLResponse)
# def read_item(request: Request, name: schema.Movie.name, db: Session = Depends(get_database_session)):
#     item = db.query(Order).filter(Order.id == name).first()
#     return templates.TemplateResponse("overview.html", {"request": request, "movie": item})
#
#
# @app.post("/movie/")
# async def create_movie(db: Session = Depends(get_database_session), name: schema.Movie.name = Form(...), url: schema.Movie.url = Form(...), rate: schema.Movie.rating = Form(...), type: schema.Movie.type = Form(...), desc: schema.Movie.desc = Form(...)):
#     movie = Order(name=name, url=url, rating=rate, type=type, desc=desc)
#     db.add(movie)
#     db.commit()
#     db.refresh(movie)
#     response = RedirectResponse('/movie', status_code=303)
#     return response
#
#
# @app.patch("/movie/{id}")
# async def update_movie(request: Request, id: int, db: Session = Depends(get_database_session)):
#     requestBody = await request.json()
#     movie = db.query(Order).get(id)
#     movie.name = requestBody['name']
#     movie.desc = requestBody['desc']
#     db.commit()
#     db.refresh(movie)
#     newMovie = jsonable_encoder(movie)
#     return JSONResponse(status_code=200, content={
#         "status_code": 200,
#         "message": "success",
#         "movie": newMovie
#     })
#
#
# @app.delete("/movie/{id}")
# async def delete_movie(request: Request, id: int, db: Session = Depends(get_database_session)):
#     movie = db.query(Order).get(id)
#     db.delete(movie)
#     db.commit()
#     return JSONResponse(status_code=200, content={
#         "status_code": 200,
#         "message": "success",
#         "movie": None
#     })
