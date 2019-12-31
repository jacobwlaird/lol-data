import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db

class LolParser(object):
    base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
    base_match_url = "https://na1.api.riotgames.com/lol/match/v4/"
    account_name_url = "summoners/by-name/"
    matches_url = "matchlists/by-account/"
    match_url = "matches/"

    config = configparser.ConfigParser()
    config.read('./general.cfg')
    max_game_index = 0

    db_host = config.get('DATABASE', 'db_id')
    db_user = config.get('DATABASE', 'db_user')
    db_pw = config.get('DATABASE', 'db_password')
    db_name = config.get('DATABASE', 'db_name')

    # db stuff.
    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_pw, db_host, db_name))
    connection = engine.connect()
    metadata = db.MetaData()

    accounts = []
    match_types = [400, 420, 440, 700]

    api_key = config.get('RIOT', 'api_key')
    new_match_data = {}

    def __init__(self):
        self.new_matches = []

    @classmethod
    def get_account_info(cls, name, start_index, end_index):
        try:
            account_response = requests.get(''.join([cls.base_summoner_url, cls.account_name_url, name, "?api_key=", cls.api_key]))
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            account_id = account_data['accountId']
            time.sleep(.2)
            player_matches_response = requests.get(''.join([cls.base_match_url, cls.matches_url, account_id, "?beginIndex=", str(start_index), "&endIndex=", str(end_index), "&api_key=", cls.api_key]))
            player_matches_response.raise_for_status()
            player_matches = json.loads(player_matches_response.text)
        except Exception as e:
            print(e)
            print("Get_account_info broke")

        return player_matches

    @classmethod
    def get_match_data(cls, match_id):
        try:
            print(''.join(["getting match data for ", str(match_id)]))
            time.sleep(.2)
            matches_response = requests.get(''.join([cls.base_match_url, cls.match_url, str(match_id), "?api_key=", cls.api_key]))
            matches_response.raise_for_status()
            cls.new_match_data[match_id] = json.loads(matches_response.text)
        except Exception as e:
            print(e)
            print("Get_match_data broke, trying again")
            time.sleep(20)
            cls.get_match_data(match_id)

        return
