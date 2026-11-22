from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, oauth2
# Proje klasöründen models.py ve schemas çağırdık. Şemaları artık buradan çekeceğiz o yüzden aşağıda Post şemasını kullandığımız her yerin adını değiştir.
# Proje klasöründen database.py içinden engine ve get_db çağırdık
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    # Bunun sayesinde her router default olarak users adresiyle ilişkili olacak, hepsine tek tek girmemize gerek kalmayacak.
    tags=["Posts"]
    # Bunun sayesinde de dokümentasyonda post işlemleri birbiriyle gruplanmış görünecek
)

# GELECEKTEN GELDİM. oauth2'de oluşturduğumuz, kullanıcı doğrulayan fonksiyonu, dependency olarak "bu işlem için giriş yapılmalı" dediğimiz her işleme gireceğiz.
# user_id: int = Depends(oauth2.get_current_user)

#################### POST İŞLEMLERİ BAŞLANGIÇ ########################

# -------------- TÜM POSTLAR --------------

# Ben postları giriş yapmdan herkes görebilir olarak yaptım. Eğer sadece giriş yapanlar ve herkes kendi post'unu görsün dersen videoda 8:29:00


@router.get("/", response_model=List[schemas.PostOUT])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # limit bir query parametresi, argüman olarak ekledik. Web sitelerinde "?"den sonra gelen kısımlarla aynı
    # typing kütüphanesinden List ekledik ve gelen response'u ona göre değiştirdik. Çünkü birden fazla post gelecek ve List içine almalıyız.
    # limit parametresini sorgumuza ekledik. limit fonksiyonu sqlalchemy'de mevcut, değer olarak sorgu anında gelmezse default 10
    # Skip(offset) de aynı mantık sayılır. search ise biraz farklı. burada title'da search yapmasını sağladık. Sırası önemli değil
    # search yaparken boşluk kullanılacaksa iki kelime arasına %20 eklemeliyiz. boşluk karakterini temsilen
    # Burada eski sorgu vardı onu yok ettim çünkü yeni sorguda vote'lar ve parametreler var
    # Burası 10. Saat sonrası ile alakalı. Vote sql sorgusunu sqlalchemy mantığına dökme kısmı.
    # select posts.id,posts.owner_id,posts.title, count(votes.post_id) as "like count" from posts LEFT JOIN votes ON posts.id=votes.post_id GROUP BY posts.id;
    # Bu sorgu ile aynı işi yapacak. Ancak mevcut response model şemamız ile uygun değil.
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

# ---------------- POST OLUŞTURMA ----------------


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # oauth2 sayfasında oluşturduğumuz get_current_user fonksiyonunu bir dependency olarak ekledik. Bu da bir insanın logged in olmasını gerektiren her durumda(post oluşturmak gibi)
    # bir token vermelerini beklememizi sağlayacak. Kısaca post oluşturabilmek giriş yapabilmeye bağlı olacak artık.
    # Foregin key null olamaz, o yüzden foreign key olacak alanın adını vererek ilişkilendirilecek alana eşitledik.
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    # Artık modele yeni alan eklersek bunu sayesinde tekrardan buraya eklemek zorunda kalmayacağız çünkü modeldeki tüm alanları dicte dönüştürüp içeriye koyacak
    # Commitlemek için aşağısı şart
    db.add(new_post)
    db.commit()
    # Refresh RETURNING * ile aynı işi görüyor. giden veriyi new_post içinde tutacak
    db.refresh(new_post)
    return new_post

# ---------------- ID'YE GÖRE POST ARAMA ----------------


@router.get("/{id}", response_model=schemas.PostOUT)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Sorguyu filtre ekleyerek gönderiyoruz. models.Post.id den gelen ile kullanıcının girdiği id'yi karşılaştırıyoruz. zaten tek bir veri dönecek o yüzden first() ile yakaladık.
    one_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not one_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} was not found")
    return one_post

# ---------------- POST SİLME -----------------


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # Yukarıdakinin aynısı, o id'ye sahip postu çektik
    # Eğer post yoksa kontrolünü first() ile yaptık
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exists")
    # Yeni eklediğimiz owner_id alanını değerlendirerek yaptığımız post giriş yapan kullanıcıya mı ait kontrolü.
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    # Silme ve commitleme adımı
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# -------------- POST GÜNCELLEME -----------------


@router.put("/{id}", response_model=schemas.PostResponse)
# Burada parametre olarak gelen ve Post modeline uydurduğumuz değişkeni updated_post olarak güncelledim çünkü içeride çakıştı
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    # Yukarıdakinin aynısı, o id'ye sahip postu çektik
    post = post_query.first()
    # Sorgudan gelen ilk postu(zaten id verdiğimiz için tek post gelecek) bir değişkene atadık
    # Eğer post gelmezse uyarı gönderdik
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exists")
        # Yeni eklediğimiz owner_id alanını değerlendirerek yaptığımız post giriş yapan kullanıcıya mı ait kontrolü.
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    # Post gelirse updated_post modeline göre güncelleyip, commitledik
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

###################### POST İŞLEMLERİ BİTİŞ ##########################
# -------------------------------------------------------------------#
