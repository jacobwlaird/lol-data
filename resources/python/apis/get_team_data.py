import pymysql
import json
import sqlalchemy as db
import configparser
import sys

def get_team_data(prod=True):

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

    team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)
    select_query = team_data_table.select().order_by(team_data_table.c.match_id.desc())
    results = connection.execute(select_query).fetchall()

    row_headers = team_data_table.c.keys()

    json_data=[]
    for result in results:
            json_data.append(dict(zip(row_headers,result)))

    if prod == True:
        return json.dumps(json_data, indent=4, default=str)
    else:
        print(json_data) 

def main():
	return get_team_data(sys.argv[1])

if __name__ == "__main__":
	main()
