import pandas as pd
import pymysql
import configparser

config = configparser.ConfigParser()
config.read('./resources/python/general.cfg')

db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

connection = pymysql.connect(db_host, db_user, db_pw, db_name)

spaynkee_matches = pd.read_sql("SELECT * FROM spaynkee_match_history", connection)
dumat_matches = pd.read_sql("SELECT * FROM dumat_match_history", connection)

recentMatch = spaynkee_matches.head(1)
print(recentMatch['role'])
