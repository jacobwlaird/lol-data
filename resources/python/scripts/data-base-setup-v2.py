import json
import csv
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData

from classes.lolparser import LolParser

# Look at the api and see what kind of info we want to keep for a particular username....
# Players -- Username based data, uuids linking to the team_match_data table 
# account_id string
# name string

# Match data
# Team data

# Create the players table
player_data_table = Table('player_data', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
player_data_table.drop(LolParser.engine)

# create the player_data table
player_data_table = Table('player_data',
        MetaData(),
        Column('account_id', String, primary_key=True),
        Column('user_name', String(40)))

player_data_table.create(LolParser.engine)

# drop the team_match_data table.
team_match_data_table = Table('team_match_data', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
team_match_data_table.drop(LolParser.engine)

# create the team_match_data table
team_match_data_table = Table('team_match_data',
        MetaData(),
        Column('match_id', BigInteger, primary_key=True),
        Column('game_version', String(40)),
        Column('win', String(10)),
        Column('participants', String(80)),
        Column('first_blood', Boolean),
        Column('first_baron', Boolean),
        Column('first_tower', Boolean),
        Column('first_dragon', Boolean),
        Column('first_inhib', Boolean),
        Column('first_rift_herald', Boolean),
        Column('dragon_kills', Integer),
        Column('rift_herald_kills', Integer), 
        Column('inhib_kills', Integer),
        Column('bans', String(80)),
        Column('enemy_bans', String(80)),
        Column('allies', String(80)),
        Column('enemies', String(80)),
        Column('start_time', TIMESTAMP), 
        Column('duration', Time))

team_match_data_table.create(LolParser.engine)

matches_table = Table('match_data', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

# Drop the matches table...
matches_table.drop(LolParser.engine)

matches_table = Table('match_data',
        MetaData(),
        Column('match_id', BigInteger, primary_key=True),
        Column('player', String(40)), # This is the new column for player foreign key? Might just use api user code or whatevr.
        Column('role', String(10)),
        Column('champion', Integer),
        Column('champion_name', String(25)),
        Column('enemy_champion', Integer),
        Column('enemy_champion_name', String(25)),
        Column('first_blood', Boolean),
        Column('first_blood_assist', Boolean),
        Column('kills', Integer),
        Column('deaths', Integer),
        Column('assists', Integer),
        Column('damage_to_champs', Integer),
        Column('damage_to_turrets', Integer),
        Column('gold_per_minute', Float), # these might need to be decimals
        Column('creeps_per_minute', Float), # same
        Column('xp_per_minute', Float), # same
        Column('wards_placed', Integer),
        Column('vision_wards_bought', Integer),
        Column('wards_killed', Integer),
        Column('items', String(200)),
        Column('perks', String(100))
        )

matches_table.create(LolParser.engine)

