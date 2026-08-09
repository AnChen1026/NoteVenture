import os

import pymysql
from configparser import ConfigParser


class SqlUtils:
    # ======================================================
    # 讀取資料庫設定（優先環境變數，其次 config.ini）
    # ======================================================
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

    def _db_setting(self, env_name, ini_key, default=None):
        value = os.environ.get(env_name)
        if value not in (None, ''):
            return value
        if self.config.has_option('DB', ini_key):
            return self.config.get('DB', ini_key)
        return default

    # ======================================================
    # 資料庫連線
    # ======================================================
    def get_connection(self):
        port_text = self._db_setting('NOTEADVENTURE_DB_PORT', 'port', '3306')
        return pymysql.connect(
            host=self._db_setting('NOTEADVENTURE_DB_HOST', 'host', 'localhost'),
            user=self._db_setting('NOTEADVENTURE_DB_USER', 'user', 'root'),
            password=self._db_setting('NOTEADVENTURE_DB_PASSWORD', 'password', ''),
            port=int(port_text),
            database=self._db_setting('NOTEADVENTURE_DB_NAME', 'database', 'music_rpg_v2'),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )

    # ======================================================
    # 查詢單一資料
    # ======================================================
    def query_one(self, sql, params = None):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()

            return result
        
        finally:
            conn.close()

    # ======================================================
    # 查詢全部資料
    # ======================================================
    def query_all(self, sql, params = None):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()

            return result

        finally:
            conn.close()

    # ======================================================
    # 新增、刪除、修改 INSERT、UPDATE、DELETE
    # ======================================================
    def execute(self, sql, params = None):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rowcount = cursor.rowcount
            conn.commit()
            return rowcount

        except Exception as e:
            conn.rollback()
            print('執行失敗', e)
            return -1

        finally:
            conn.close()

    # ======================================================
    # 多句 SQL 在同一個 transaction，全部成功才 commit
    # sql_list 格式：[(sql, params), (sql, params)]
    # ======================================================
    def execute_transaction(self, sql_list):
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                for sql, params in sql_list:
                    cursor.execute(sql, params)
            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print('執行失敗', e)
            return False

        finally:
            conn.close()

