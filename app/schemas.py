from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated


#################### POST İŞLEMLERİ BAŞLANGIÇ ########################


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# Her işlem için create/update farklı şema oluşturabiliriz.
# Bunun sayesinde Post oluştururken 3 veri gerekli iken, post güncellerken kullanıcının sadece 1 veri verebileceğini söyleyebiliriz.

# Yeni classları üstteki PostBase üzerinden oluşturabiliriz.


class PostCreate(PostBase):
    pass
    # Post oluştururken PostBase içinde ne varsa onu kullanacak demek.


class PostUpdate(PostBase):
    content: str
    published: bool

# Yukarısı kullanıcının bize göndereceği verinin şemasını oluşturuyordu.
# Aşağıya bizim kullanıcıya geri göndereceğimiz verinin şemasını oluşturalım.


class PostResponse(PostBase):
    # title,content,published inheritlediğimiz için PostBase sınıfından gelecek o yüzden tekrar yazmamıza gerek yok.
    id: int
    owner_id: int
    created_at: datetime
    # models.py'de oluşturduğumuz owner ile aynı. UserResponse alarak da hangi kısımları döndüreceğimizi söyledik. pydantic şart
    owner: UserResponse

    # Bunu yapmazsak response olarak dönen veriler pydantic'in anlayacağı türden yani dict olmuyor. Bu şart.
    class Config:
        from_attributes = True

# Bu yukarıdaki ile aynı görevi yapacak ancak Vote sistemi ile oluşan pydantic beklentisini destekleyecek şekilde olacak.


class PostOUT(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        from_attributes = True

###################### POST İŞLEMLERİ BİTİŞ ##########################
# --------------------------------------------------------------------#
#################### USER İŞLEMLERİ BAŞLANGIÇ ########################


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    # UserCreate'dan inherit almıyoruz çünkü onun içinde password olduğu için onu da direkt çekecek.
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    # Kullanıcı girişinde kullanılcak şema
    email: EmailStr
    password: str


class Token(BaseModel):
    # Oluşacak tokenda kullanılacak şema
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


###################### USER İŞLEMLERİ BİTİŞ ##########################
# --------------------------------------------------------------------#
#################### VOTE İŞLEMLERİ BAŞLANGIÇ ########################

class Vote(BaseModel):
    # Hocanın gösterdiği conint artık tavsiye edilmiyormuş. Onun yerine Annotated ve içindeki şartlar için Field importladık.
    post_id: int
    dir: Annotated[int, Field(ge=0, le=1)]
