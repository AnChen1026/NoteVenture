import pymysql
from configparser import ConfigParser

class SqlUtils:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini", encoding="utf-8")

    # 資料庫連線
    def get_connection(self):
        return pymysql.connect(
            host=self.config.get("DB", "host"),
            user=self.config.get("DB", "user"),
            password=self.config.get("DB", "password"),
            port=self.config.getint("DB", "port"),
            database=self.config.get("DB", "database"),
            cursorclass=pymysql.cursors.DictCursor
        )

    # 查詢單一資料
    def query_one(self, sql, params = None):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()

            return result
        
        finally:
            conn.close()

    # 查詢全部資料
    def query_all(self, sql, params = None):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()

            return result

        finally:
            conn.close()

    # 新增、刪除、修改 INSERT、UPDATE、DELETE 
    def execute(self, sql, params = None):
            conn = self.get_connection()
    
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)

                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                print('執行失敗', e)
                return False

            finally:
                conn.close()

