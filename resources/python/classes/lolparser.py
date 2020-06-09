import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
from sqlalchemy import orm

class LolParser(object):
    base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
    base_match_url = "https://na1.api.riotgames.com/lol/match/v4/"
    account_name_url = "summoners/by-name/"
    matches_url = "matchlists/by-account/"
    match_url = "matches/"

    config = configparser.ConfigParser()
    config.read('./general.cfg')
    max_game_index = 7000 

    db_host = config.get('DATABASE', 'db_id')
    db_user = config.get('DATABASE', 'db_user')
    db_pw = config.get('DATABASE', 'db_password')
    db_name = config.get('DATABASE', 'db_name')

    # db stuff.
    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(db_user, db_pw, db_host, db_name), pool_size=100, max_overflow = 100)
    connection = engine.connect()
    metadata = db.MetaData()
    sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)

    champs_table = db.Table('champions', metadata, autoload=True, autoload_with=engine)
    match_data_table = db.Table('match_data', metadata, autoload=True, autoload_with=engine)
    team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)
    items_table = db.Table('items', metadata, autoload=True, autoload_with=engine)
    json_data_table = db.Table('json_data', metadata, autoload=True, autoload_with=engine)

    accounts = ['spaynkee', 'dumat', 'archemlis', 'stylus_crude', 'dantheninja6156', 'csqward'] 
    match_types = [400, 410, 420, 440, 700] # make sure this includes new types of matchmade games.

    api_key = config.get('RIOT', 'api_key')
    new_match_data = {}

    def __init__(self):
        self.new_matches = []

    @classmethod
    def get_account_info(cls, name, account_id, start_index, end_index):
        try:
            player_matches = {}
            player_matches_response = requests.get(''.join([cls.base_match_url, cls.matches_url, account_id, "?beginIndex=", str(start_index), "&endIndex=", str(end_index), "&api_key=", cls.api_key]))
            player_matches_response.raise_for_status()
            player_matches = json.loads(player_matches_response.text)
        except Exception as e:
            print("Get_account_info broke")
            if e.response.status_code == 403:
                print("Api key is probably expired")
            else:
                print(e)

            if e.response.status_code == 429:
                print("Well that's an unfortunate timeout. I gotchu though fam.")
                time.sleep(20)
                return cls.get_account_info(name, account_id, start_index, end_index)

        return player_matches

    @classmethod
    def get_match_data(cls, match_id):
        try:
            print(''.join(["getting match data for ", str(match_id)]))
            time.sleep(.2)
            matches_response = requests.get(''.join([cls.base_match_url, cls.match_url, str(match_id), "?api_key=", cls.api_key]))
            matches_response.raise_for_status()
            match_json = json.loads(matches_response.text)
            cls.new_match_data[match_id] = match_json

            # Yes, I know we just turned this into json, but we actually need the raw text to store into the db.
            return matches_response.text
        except Exception as e:
            print(e)
            print("Get_match_data broke, trying again")
            time.sleep(20)
            cls.get_match_data(match_id)

        return

    @classmethod
    def store_json_data(cls, match, json_formatted_string):
        json_sql_insert = db.insert(cls.json_data_table).values(match_id=match, 
                json_data=json_formatted_string)

        results = cls.connection.execute(json_sql_insert)
        return
