# Kullanıcı şifrelerini hash'lamak için kullanacağız.
import bcrypt


# Hashing modelini bcrypt algoritmasını kullanarak değişkene atayamadım çünkü versiyon farkından dolayı sorun çıkartıyor.
# Onun yerine fonksiyon içinde yaptım.


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Kullanıcıdan gelen şifre ile, hash edilmiş şifreyi karşılaştırıp doğrulayacak fonksiyon.


def verify(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
