from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=["Authentication"])

# Kullanıcı auth.py üzerinden giriş yapar, auth.py ona bir JWT Token geri döndürür. Kullanıcı sonraki işlemlerde şifre ile değil token ile onay alır.
# Aynı zamanda auth.py o token'ın gerçek olup olmadığını kontrol eder.


@router.post('/login', response_model=schemas.Token)
# Bu sefer şema kullanmadık çünkü FastAPI JSON beklerdi. OAuth2 veriyi form olarak gönderir ve bu arayüzdeki butonla tam uyumluluk sağlar.
# Postman'de raw JSON olarak değil de, form data olarak gönderiyoruz o yüzden bu işlemde
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # Token oluşturma ve geri döndürme
    # Payload'ı burada gönderiyoruz. Şu an sadece kullanıcı adını gönderdik payload olarak.
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
