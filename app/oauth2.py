from jose import jwt, JWTError
# Kurstan farklı olarak utcnow yerine timezone ekleyip, utc'yi öyle seçiyoruz.
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, database, models, config


# Login endpoint'i yani auth.py'de bulunan path operation'un adresini ekliyoruz. Bu token oluşturacak ve doğrulanması gereken giriş bilgileri bu adreste demek.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Token burada oluşacak.
# SECRET_KEY
# Algorithm(HS256)
# Token geçerlilik süresi. Bunlar gerekli olan şeyler.

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.access_token_expire_minutes

# Bir "Payload" olacağı için onu tokenın içine atacağız, dict tipindeki data değişkeninde olacak


def create_access_token(data: dict):
    # Dışarıdan gelen data'ya dokunmadan kopyasını oluşturduk.
    to_encode = data.copy()
    # Şu anki zamanın üzerine belirlediğimiz süreyi ekleyecek. Yani şimdiki zamandan şu kadar zaman sonrasında token geçersiz olsun.
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Dict içine exp key'i altında expiration zamanını ekledik.
    to_encode.update({"exp": expire})

    # Gerekli olan her şeyi vererek jwt'nin token oluşturmasını sağladık ve geri döndürdük.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # Yukarıda nasıl encode ettiysek, burada aynı şekilde decode ediyoruz.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # login fonksiyonundan gelen id'yi burada bir değişkene ayırdık.
        id = str(payload.get("user_id"))
        if id is None:
            raise credentials_exception
        # token_data içinde kullanıcının veritabanındaki id'si var. Bu şu an lazım değil ama önümüzdeki aşamalarda gerekeceği için elimizde tuttuk.
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # Bu fonksiyon otomatik olarak  'login' sayfasında oluşan Token'ı çekecek, verify_access_token çağırıp doğrulayacak, id'yi bizim için çıkartacak ve istersek kullanıyıcı id'ye göre
    # veritabanından çekebileceğiz ve path operation fonksiyonlarımıza parametre olarak göndermemizi sağlayacak.
    # Yanlış giriş bilgisi olduğunda oluşmasının istediğimiz hatayı kurduk.
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    # id kısmı verify_access_token'dan geliyor. token ise "login" sayfasından. Doğru giriş yapılıp token oluşursa verify_access_token return olacak zaten.
    # token doğru mu kontrolünü burası yapmıyor. Burası token doğru olsa da, olmasa da kullanıcıyı alıyor ve doğru olmaması durumunda oluşmasını istediğimiz hata ile birlikte döndürüyor.
    token = verify_access_token(token, credentials_exception)
    # Burada verify_access_token'dan gelen id, veritabanındaki o id ile uyuşan kullanıcıyı alıp değişkene atıyoruz.
    user = db.query(models.User).filter(
        models.User.id == int(token.id)).first()
    return user
