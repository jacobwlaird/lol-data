import sqlalchemy as db
import configparser
from sqlalchemy import orm
from sys import argv
from sys import exit
import pandas as pd
from classes.lolparser import LolParser
import math
import time
import datetime
import numpy as np
import pymysql
import os
import json

# this script is gonna parse through the json table, get our info, and backfill our table.
config = configparser.ConfigParser()
config.read('./resources/python/general.cfg')

db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_pw, db_host, db_name), pool_size=100, max_overflow = 100)
connection = engine.connect()
metadata = db.MetaData()
sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)

team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)

old_data = {} 

select_old_data = "SELECT * FROM team_data;"
old_data = pd.read_sql(select_old_data, LolParser.connection)

new_data = {}

select_new_data = "SELECT * FROM json_data;"
new_data = pd.read_sql(select_new_data, LolParser.connection)

for row in new_data['match_id']:   
    print("Updating match {}".format(row))

    if old_data[old_data['match_id'] == row] is not None:
        json_dict = json.loads(new_data[new_data['match_id'] == row]['json_data'].values[0])

        teams = json_dict['teams']
        game_result = old_data[old_data['match_id'] == row]['win'].values[0]

        our_team = {}
        enemy_team = {}

        if teams[0]['win'] == game_result:
            our_team = teams[0]
            enemy_team = teams[1]
        else:
            our_team = teams[1]
            enemy_team = teams[0]

        enemy_dragon_kills = enemy_team['dragonKills']
        enemy_rift_herald_kills = enemy_team['riftHeraldKills']

        team_data_table_update = db.update(LolParser.team_data_table).values(
           enemy_dragon_kills=enemy_dragon_kills,
           enemy_rift_herald_kills=enemy_rift_herald_kills
        ).where(LolParser.team_data_table.c.match_id==row)

        results = LolParser.connection.execute(team_data_table_update)
    else:
       print("Hey, uh, {} isn't in our team_data table. Fix me sometime?".format(row))
       continue

exit()
