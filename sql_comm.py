import sqlite3
from threading import Lock
conn = sqlite3.connect(r"cat_database.db", check_same_thread=False)
cursor = conn.cursor()
lock = Lock()
def get_parent_cat():
    lock.acquire(True)
    parent_cat = cursor.execute('''
    SELECT DISTINCT parent_id, parent_name FROM categories
    WHERE parent_name != 'NA'
    ''').fetchall()
    lock.release()
    return [{"label": cat[1], "value": cat[0]} for cat in parent_cat]

def get_sub_cat(parent_cat):
    lock.acquire(True)
    sub_cat = cursor.execute(f'''
    SELECT category_id, name FROM categories
    WHERE parent_id == {parent_cat}
    ''').fetchall()
    lock.release()
    return [{"label": cat[1], "value": cat[0]} for cat in sub_cat]

def get_ser_options(category):
    lock.acquire(True)
    seriess = cursor.execute(f'''
    SELECT id, name FROM series
    WHERE category_id == {category}
    ''').fetchall()
    lock.release()
    return [{"label": ser[1], "value": ser[0]} for ser in seriess]

def get_ser_dict(series_id, category):
    lock.acquire(True)
    ser_data = cursor.execute(f'''
    SELECT name, database FROM series
    WHERE category_id == '{category}'
    AND id == '{series_id}'
    ''').fetchone()
    lock.release()
    return {series_id: ser_data[1]}, ser_data[0]

def search_all_ser(search_str):
    lock.acquire(True)
    search_substrs = search_str.split(" ")
    query_str = '''
    SELECT id, name, database FROM series
    WHERE  
    '''
    for i, substr in enumerate(search_substrs):
        if i > 0:
            query_str += " AND"
        query_str += f" name like '%{substr}%'"
        if i == len(search_substrs) - 1:
            query_str += " LIMIT 250"

    search_data = cursor.execute(query_str).fetchall()
    lock.release()
    return list(map(lambda ser: {"label": ser[1], "value": str([ser[0], ser[1], ser[2]])}, search_data))