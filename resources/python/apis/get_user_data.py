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

    match_data_table = db.Table('match_data', metadata, autoload=True, autoload_with=engine)
	# select where player is name
    select_query = match_data_table.select().where(match_data_table.c.player == name).order_by(match_data_table.c.match_id.desc())
    results = connection.execute(select_query).fetchall()

    row_headers = match_data_table.c.keys()

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
