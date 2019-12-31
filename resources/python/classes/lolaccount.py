import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
from .lolparser import LolParser

class LolAccount(object):
    def __init__(self, name):
        self.account_name = name
        self.game_index = 0
        self.user_matches = []
        self.previous_player_matches = []
        self.new_player_matches = []

    #This saves the users previous matches, and new matches to be added.
    def get_user_matches(self):
        while self.game_index < LolParser.max_game_index:
            self.add_user_match_history(self.game_index, self.game_index+100) 
            if not self.user_matches:
                break

            self.game_index += 100

    # sets the previous_matches and new_player_matches properties.
    def add_user_match_history(self, start_index=0, end_index=100):
        player_matches = LolParser.get_account_info(self.account_name, start_index, end_index)
        select_previous_matches = "SELECT match_id FROM {}_match_history;".format(self.account_name)
        player_match_history = pd.read_sql(select_previous_matches, LolParser.connection)

        for match in player_match_history['match_id']:
            self.previous_player_matches.append(match)

        # could maybe improve this by just selecting games that are in user table but not in matches
        for match in player_matches['matches']:
            if str(match['gameId']) not in self.previous_player_matches and match['gameId'] > 200000000:
                if match['queue'] in LolParser.match_types:
                    if match['role'] == 'DUO_SUPPORT':
                        lane = "SUPPORT"
                    else:
                        lane = match['lane']

                    user_table = db.Table('{}_match_history'.format(self.account_name), LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
                    match_sql_insert = db.insert(user_table).values(match_id=match['gameId'], role=lane, champion=match['champion'])

                    results = LolParser.connection.execute(match_sql_insert)
                    self.user_matches.append(match['gameId'])
        return
