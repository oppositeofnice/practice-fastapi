from fastapi import FastAPI
# Bu farklı domainlerden sitemize erişilebilmesini sağlamak için kullanacağımız bir şey.
from fastapi.middleware.cors import CORSMiddleware


from . import models
from .database import engine
from .routers import posts, users, auth, vote
from .config import settings

# Modelimizi engine kullanarak maine çektik
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS. Burada API ile konuşabilecek domainleri giriyoruz. origins
origins = ["https://www.google.com"]
# Artık kullanıcılar google üzerinden API'ımız ile konuşabilecek.

# CORS.  CORS, tarayıcının bir web sayfasının farklı bir adresteki (domain/port) API’ye istek atmasına izin verip vermeyeceğini belirleyen güvenlik kuralıdır;
# FastAPI’de CORSMiddleware ile hangi adreslerin API’ne erişebileceğini biz belirleriz.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # Belirli methodları yasaklayıp, serbest bırakabiliriz. Dış adresten gelenler GET kullanabilsin ancak POST kullanamasın gibi.
    allow_methods=["*"],
    allow_headers=["*"],
)


# main.py çok dolduğu için users ve posts işlemlerini ilgili .py dosyalarına taşıyıp, routerlar ile kullanıyoruz artık 6:25:00

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
