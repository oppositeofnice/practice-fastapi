from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
# Proje klasöründen models.py ve schemas çağırdık. Şemaları artık buradan çekeceğiz o yüzden aşağıda Post şemasını kullandığımız her yerin adını değiştir.
# Proje klasöründen database.py içinden engine ve get_db çağırdık
from ..database import get_db

router = APIRouter(
    prefix="/users",
    # Bunun sayesinde her router default olarak users adresiyle ilişkili olacak, hepsine tek tek girmemize gerek kalmayacak.
    tags=["Users"]
    # Bunun sayesinde de dokümentasyonda user işlemleri birbiriyle gruplanmış görünecek
)
# artık @app yerine @router kullanabiliriz

#################### USER İŞLEMLERİ BAŞLANGIÇ ########################

# ---------- KULLANICIDAN GELEN VERİ İLE HESAP OLUŞTURMA -------------


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # şifreyi hash'le - user.password'den gelecek
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    # Email ve şifre user pydantic değişkeninde UserCreate şemasında tutulacak.
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# ----------------- ID İLE KULLANICI ARAMA -----------------------


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user {id} does not exist")
    return user
