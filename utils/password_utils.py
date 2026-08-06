# password_utils.py
import bcrypt

# ======================================================
# 將密碼雜湊
# ======================================================
def hash_password(password):
    return bcrypt.hashpw(               # bcrypt.hashpw(密碼位元組, salt)將密碼產生雜湊
        password.encode("utf-8"),       # 將 str 轉成 bytes 位元組
        bcrypt.gensalt()                # bcrypt.gensalt()產生一個隨機資料
    ).decode("utf-8")                   # 將 bytes 轉回 str


# ======================================================
# 檢查密碼
# ======================================================
def check_password(password, password_hash):
    return bcrypt.checkpw(              # bcrypt.checkpw() 檢查密碼 回傳bool值
        password.encode("utf-8"),       
        password_hash.encode("utf-8")   
    )