from db import SqlUtils
from pprint import pprint

db = SqlUtils()

sql = """
SELECT * FROM teacher;
"""

result = db.query_one(sql)
pprint(result, sort_dicts=False)


def create_student():
    sql = """
    INSERT INTO student ()
    """