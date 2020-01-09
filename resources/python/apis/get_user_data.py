import pymysql
import json
import sqlalchemy as db
import configparser
import sys

def get_data(name, prod=True):

    config = configparser.ConfigParser()

    if prod == True:
        config.read('./resources/python/general.cfg')
    else:
        config.read('../general.cfg')

    db_host = config.get('DATABASE', 'db_id')
    db_user = config.get('DATABASE', 'db_user')
    db_pw = config.get('DATABASE', 'db_password')
    db_name = config.get('DATABASE', 'db_name')

    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_pw, db_host, db_name))
    connection = engine.connect()
    metadata = db.MetaData()

    user_table = db.Table('{}_match_history'.format(name), metadata, autoload=True, autoload_with=engine)
    select_query = user_table.select()
    results = connection.execute(select_query).fetchall()

    row_headers = user_table.c.keys()

    json_data=[]
    for result in results:
            json_data.append(dict(zip(row_headers,result)))

    if prod == True:
        return json.dumps(json_data, indent=4, default=str)
    else:
        print(json_data) # maybe we want to ?

def main():

	return get_data(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
	main()
