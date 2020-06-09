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

accounts = ['spaynkee', 'dumat', 'archemlis', 'stylus_crude', 'dantheninja6156', 'csqward']

config = configparser.ConfigParser()
config.read('./general.cfg')

db_host = config.get('DATABASE', 'db_id')
db_user = config.get('DATABASE', 'db_user')
db_pw = config.get('DATABASE', 'db_password')
db_name = config.get('DATABASE', 'db_name')

engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_pw, db_host, db_name), pool_size=100, max_overflow = 100)
connection = engine.connect()
metadata = db.MetaData()
sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)
matches_table = db.Table('matches', metadata, autoload=True, autoload_with=engine)
match_data_table = db.Table('match_data', metadata, autoload=True, autoload_with=engine)
team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)

for account in accounts:
    old_data = {} 

    select_old_data = "SELECT * FROM {}_match_history;".format(account)
    old_data = pd.read_sql(select_old_data, LolParser.connection)

    new_data = {}

    select_new_data = "SELECT * FROM match_data WHERE `player` = '{}'".format(account)
    new_data = pd.read_sql(select_new_data, LolParser.connection)

    for row in old_data['match_id']:   
        if new_data[new_data['match_id'] == row].empty:
           old_match_data = old_data[old_data['match_id'] == row]

           # Handle columns that are supposed to be a number but we dont have data for
           if math.isnan(old_match_data['enemy_champion'].item()):
               old_match_data['enemy_champion'] = None

           if math.isnan(old_match_data['xp_per_minute'].item()):
               old_match_data['xp_per_minute'] = None

           new_stats_insert = db.insert(LolParser.match_data_table).values( 
                   match_id=old_match_data['match_id'].item(),
                   player=account,
                   champion=old_match_data['champion'].item(),
                   kills=old_match_data['kills'].item(),
                   deaths=old_match_data['deaths'].item(),
                   assists=old_match_data['assists'].item(),
                   role=old_match_data['role'].item(),
                   wards_placed=old_match_data['wards_placed'].item(),
                   damage_to_champs=old_match_data['damage_to_champs'].item(),
                   damage_to_turrets=old_match_data['damage_to_turrets'].item(),
                   vision_wards_bought=old_match_data['vision_wards_bought'].item(),
                   gold_per_minute=old_match_data['gold_per_minute'].item(),
                   creeps_per_minute=old_match_data['creeps_per_minute'].item(),
                   xp_per_minute=old_match_data['xp_per_minute'].item(),
                   champion_name=old_match_data['champion_name'].item(),
                   enemy_champion=old_match_data['enemy_champion'].item(),
                   enemy_champion_name=old_match_data['enemy_champion_name'].item(),
                   first_blood=old_match_data['first_blood'].item(),
                   first_blood_assist=old_match_data['first_blood_assist'].item(),
                   items=old_match_data['items'].item(),
                   perks=old_match_data['perks'].item(),
                   wards_killed=old_match_data['wards_killed'].item())
           results = LolParser.connection.execute(new_stats_insert)
        else:
           print("{} is already in there for {}".format(row, account))
           continue

# now we do the team_data table
old_teams_data = {} 

select_old_teams_data = "SELECT * FROM matches;"
all_old_teams_data = pd.read_sql(select_old_teams_data, LolParser.connection)

new_teams_data = {}

select_new_teams_data = "SELECT * FROM team_data;"
new_teams_data = pd.read_sql(select_new_teams_data, LolParser.connection)

for row in all_old_teams_data['match_id']:   
    # if the row isn't in the new table, add it
    if new_teams_data[new_teams_data['match_id'] == row].empty:
       old_teams_data = all_old_teams_data[all_old_teams_data['match_id'] == row]
       old_teams_data = old_teams_data.replace({np.nan: None})

       team_data_table_insert = db.insert(LolParser.team_data_table).values(match_id=row, 
           participants=old_teams_data['participants'].item(),
           win=old_teams_data['win'].item(),
           first_blood=old_teams_data['first_blood'].item(),
           first_baron=old_teams_data['first_baron'].item(),
           first_tower=old_teams_data['first_tower'].item(),
           first_rift_herald=old_teams_data['first_rift_herald'].item(),
           rift_herald_kills=old_teams_data['rift_herald_kills'].item(),
           first_dragon=old_teams_data['first_dragon'].item(),
           dragon_kills=old_teams_data['dragon_kills'].item(),
           first_inhib=old_teams_data['first_inhib'].item(),
           inhib_kills=old_teams_data['inhib_kills'].item(),
           bans=old_teams_data['bans'].item(),
           enemy_bans=old_teams_data['enemy_bans'].item(),
           game_version=old_teams_data['game_version'].item(),
           allies=old_teams_data['allies'].item(),
           enemies=old_teams_data['enemies'].item(),
           start_time=old_teams_data['start_time'].iloc[0].to_pydatetime(),
           duration=old_teams_data['duration'].iloc[0].to_pytimedelta()
           )

       results = LolParser.connection.execute(team_data_table_insert)
    else:
       print("We already have team data for {}".format(row))
       continue


exit()
