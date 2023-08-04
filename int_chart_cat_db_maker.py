<<<<<<< HEAD
import io
import zipfile
import nasdaqdatalink as ndl
import pandas as pd
import requests
from full_fred.fred import Fred as Fred2
import sqlite3
import csv
conn = sqlite3.connect(r"cat_database.db")
cursor = conn.cursor()
#cursor.execute("DROP TABLE categories")
#cursor.execute("DROP TABLE series")
cursor.execute('''
CREATE TABLE categories(
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER NOT NULL,
    parent_name TEXT NOT NULL,
    gparent_id INTEGER NOT NULL,
    database TEXT NOT NULL);
''')
cursor.execute('''
CREATE TABLE series(
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    database TEXT NOT NULL
)
''')
ndl.ApiConfig.api_key = "HP2mLCTfC38KJsseJSos"
fred_series = Fred2("fredapikey.txt")
r = requests.get(
    "https://raw.githubusercontent.com/joshuaulrich/freddy-mcfredface/master/all_fred_categories_and_parents.csv")
fred_categories_df = pd.read_csv(io.StringIO(r.text))
fred_data = csv.reader(io.StringIO(r.text))
next(fred_data)
cursor.executemany("INSERT OR IGNORE INTO categories (category_id, name, parent_id, parent_name, gparent_id, database) VALUES(?, ?, ?, ?, ?, 'FRED')", fred_data)
rows = cursor.execute("SELECT * FROM categories LIMIT 5").fetchall()
conn.commit()
r2 = requests.get("https://data.nasdaq.com/api/v3/databases/?api_key=HP2mLCTfC38KJsseJSos")
nasdaq_categories_df = pd.DataFrame(r2.json()["databases"]).query("premium == False").reset_index()
nasdaq_categories_df["id"] = nasdaq_categories_df["id"] + 40000
nasdaq_categories_df["parent_name"] = ["Commodity Based", "Money, Banking, & Finance", "Academic Data",
                                    "Blockchain",
                                    "Academic Data", "Blockchain", "Commodity Based",
                                    "Money, Banking, & Finance",
                                    "Blockchain", "International Data", "Academic Data", "International Data",
                                    "Money, Banking, & Finance", "Money, Banking, & Finance",
                                    "Money, Banking, & Finance", "Interest Rates", "International Data",
                                    "International Data",
                                    "Prices", "Money, Banking, & Finance", "Prices", "Money, Banking, & Finance",
                                    "International Data", "Money, Banking, & Finance", "Academic Data",
                                    "Money, Banking, & Finance", "International Data",
                                    "Production and Business Activity",
                                    "Money, Banking, & Finance", "Consumer opinion surveys",
                                    "Money, Banking, & Finance", "Academic Data", "Institutions", "Institutions",
                                    "Money, Banking, & Finance"]
nasdaq_categories_df["parent_id"] = [33583, 32991, 33060, 50000, 33060, 50000, 33583, 32991, 50000, 32263, 33060, 32263, 32991, 32991,
                                     32991, 22, 32263, 32263, 32455, 32991, 32455, 32991, 32263, 32991, 33060, 32991, 32263, 1, 32991,
                                     33261, 32991, 33060, 32956, 32956, 32991]
nasdaq_categories_df["gparent_id"] = [{"33583": 31, "32991": 0, "33060": 0, "50000": 0, "32263": 0, "22": 32991, "32455": 0, "1": 0, "33261": 33265, "32956": 32263}[f"{id}"] for id in nasdaq_categories_df["parent_id"]]
nasdaq_categories_df[["name", "id", "parent_id", "parent_name", "gparent_id", "database_code"]].rename({"id":"category_id", "database_code": "database"}, axis = 1).to_sql("categories", con=conn, if_exists='append', index=False)
categories_dict = {}
all_series_options = {}
for pcategory_name in pd.unique(fred_categories_df["parent_name"].values):
    print(pcategory_name)
    if pcategory_name not in ["Counties", "MSAs", "Parishes"]:
        for index, row in fred_categories_df.loc[fred_categories_df["parent_name"] == pcategory_name, :].iterrows():
            cat_dict = fred_series.get_series_in_a_category(row["id"], order_by="popularity")
            if cat_dict is not None and "seriess" in cat_dict.keys() and len(cat_dict["seriess"]) > 0 and row["name"]:
                df = pd.DataFrame(cat_dict["seriess"])
                if not df.empty:
                    cursor.executemany(f"INSERT OR IGNORE INTO series (id, name, category_id, database) VALUES (?, ?, {row['id']}, 'FRED')", df[["id", "title"]].values.tolist())
                else:
                    cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
            else:
                cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")  
    else:
        print(f"Deleting {pcategory_name}")
        cursor.execute(f"DELETE FROM categories WHERE parent_name == '{pcategory_name}'")  
for index, row in nasdaq_categories_df.iterrows():
    print(row['name'], row['parent_name'])
    try:
        zipdata = zipfile.ZipFile(io.BytesIO(requests.get(
            f"https://data.nasdaq.com/api/v3/databases/{row['database_code']}/metadata?api_key=HP2mLCTfC38KJsseJSos").content))
        df = pd.read_csv(zipdata.open(zipdata.namelist()[0]))
        if row["name"] not in ["Federal Reserve Economic Data", "London Bullion Market Association"] and not df.empty:
            cursor.executemany(f"INSERT OR IGNORE INTO series (id, name, category_id, database) VALUES (?, ?, '{row['id']}', '{row['database_code']}')", df[["code", "name"]].values.tolist())
        else:
            cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
    except zipfile.BadZipFile:
        cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
conn.commit()
for row in cursor.execute("SELECT * FROM series LIMIT 15").fetchall():
    print(row)
=======
import io
import zipfile
import nasdaqdatalink as ndl
import pandas as pd
import requests
from full_fred.fred import Fred as Fred2
import sqlite3
import csv
conn = sqlite3.connect(r"cat_database.db")
cursor = conn.cursor()
#cursor.execute("DROP TABLE categories")
#cursor.execute("DROP TABLE series")
cursor.execute('''
CREATE TABLE categories(
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER NOT NULL,
    parent_name TEXT NOT NULL,
    gparent_id INTEGER NOT NULL,
    database TEXT NOT NULL);
''')
cursor.execute('''
CREATE TABLE series(
    category_id INTEGER NOT NULL,
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    database TEXT NOT NULL
)
''')
cursor.execute("""
CREATE INDEX category_id ON series (category_id)
""")
ndl.ApiConfig.api_key = "HP2mLCTfC38KJsseJSos"
fred_series = Fred2("fredapikey.txt")
r = requests.get(
    "https://raw.githubusercontent.com/joshuaulrich/freddy-mcfredface/master/all_fred_categories_and_parents.csv")
fred_categories_df = pd.read_csv(io.StringIO(r.text))
fred_data = csv.reader(io.StringIO(r.text))
next(fred_data)
cursor.executemany("INSERT OR IGNORE INTO categories (category_id, name, parent_id, parent_name, gparent_id, database) VALUES(?, ?, ?, ?, ?, 'FRED')", fred_data)
rows = cursor.execute("SELECT * FROM categories LIMIT 5").fetchall()
conn.commit()
r2 = requests.get("https://data.nasdaq.com/api/v3/databases/?api_key=HP2mLCTfC38KJsseJSos")
nasdaq_categories_df = pd.DataFrame(r2.json()["databases"]).query("premium == False").reset_index()
nasdaq_categories_df["id"] = nasdaq_categories_df["id"] + 40000
nasdaq_categories_df["parent_name"] = ["Commodity Based", "Money, Banking, & Finance", "Academic Data",
                                    "Blockchain",
                                    "Academic Data", "Blockchain", "Commodity Based",
                                    "Money, Banking, & Finance",
                                    "Blockchain", "International Data", "Academic Data", "International Data",
                                    "Money, Banking, & Finance", "Money, Banking, & Finance",
                                    "Money, Banking, & Finance", "Interest Rates", "International Data",
                                    "International Data",
                                    "Prices", "Money, Banking, & Finance", "Prices", "Money, Banking, & Finance",
                                    "International Data", "Money, Banking, & Finance", "Academic Data",
                                    "Money, Banking, & Finance", "International Data",
                                    "Production and Business Activity",
                                    "Money, Banking, & Finance", "Consumer opinion surveys",
                                    "Money, Banking, & Finance", "Academic Data", "Institutions", "Institutions",
                                    "Money, Banking, & Finance"]
nasdaq_categories_df["parent_id"] = [33583, 32991, 33060, 50000, 33060, 50000, 33583, 32991, 50000, 32263, 33060, 32263, 32991, 32991,
                                     32991, 22, 32263, 32263, 32455, 32991, 32455, 32991, 32263, 32991, 33060, 32991, 32263, 1, 32991,
                                     33261, 32991, 33060, 32956, 32956, 32991]
nasdaq_categories_df["gparent_id"] = [{"33583": 31, "32991": 0, "33060": 0, "50000": 0, "32263": 0, "22": 32991, "32455": 0, "1": 0, "33261": 33265, "32956": 32263}[f"{id}"] for id in nasdaq_categories_df["parent_id"]]
nasdaq_categories_df[["name", "id", "parent_id", "parent_name", "gparent_id", "database_code"]].rename({"id":"category_id", "database_code": "database"}, axis = 1).to_sql("categories", con=conn, if_exists='append', index=False)
categories_dict = {}
all_series_options = {}
for pcategory_name in pd.unique(fred_categories_df["parent_name"].values):
    print(pcategory_name)
    if pcategory_name not in ["Counties", "MSAs", "Parishes"]:
        for index, row in fred_categories_df.loc[fred_categories_df["parent_name"] == pcategory_name, :].iterrows():
            cat_dict = fred_series.get_series_in_a_category(row["id"], order_by="popularity")
            if cat_dict is not None and "seriess" in cat_dict.keys() and len(cat_dict["seriess"]) > 0 and row["name"]:
                df = pd.DataFrame(cat_dict["seriess"])
                if not df.empty:
                    cursor.executemany(f"INSERT OR IGNORE INTO series (id, name, category_id, database) VALUES (?, ?, {row['id']}, 'FRED')", df[["id", "title"]].values.tolist())
                else:
                    cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
            else:
                cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")  
    else:
        print(f"Deleting {pcategory_name}")
        cursor.execute(f"DELETE FROM categories WHERE parent_name == '{pcategory_name}'")  
for index, row in nasdaq_categories_df.iterrows():
    print(row['name'], row['parent_name'])
    try:
        zipdata = zipfile.ZipFile(io.BytesIO(requests.get(
            f"https://data.nasdaq.com/api/v3/databases/{row['database_code']}/metadata?api_key=HP2mLCTfC38KJsseJSos").content))
        df = pd.read_csv(zipdata.open(zipdata.namelist()[0]))
        if row["name"] not in ["Federal Reserve Economic Data", "London Bullion Market Association"] and not df.empty:
            cursor.executemany(f"INSERT OR IGNORE INTO series (id, name, category_id, database) VALUES (?, ?, '{row['id']}', '{row['database_code']}')", df[["code", "name"]].values.tolist())
        else:
            cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
    except zipfile.BadZipFile:
        cursor.execute(f"DELETE FROM categories WHERE category_id == '{row['id']}'")
conn.commit()
for row in cursor.execute("SELECT * FROM series LIMIT 15").fetchall():
    print(row)
>>>>>>> 70d0c6876fcc65d16a9ee7764662b7c79d45eea0
