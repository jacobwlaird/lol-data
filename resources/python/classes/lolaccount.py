import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
from sqlalchemy import orm
from .lolparser import LolParser

class LolAccount(object):
    def __init__(self, name):
        self.account_name = name
        self.game_index = 0
        self.user_matches = []
        self.previous_player_matches = []
        self.user_table = db.Table('{}_match_history'.format(self.account_name), LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

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

                    match_sql_insert = db.insert(self.user_table).values(match_id=match['gameId'], role=lane, champion=match['champion'])

                    results = LolParser.connection.execute(match_sql_insert)
                    self.user_matches.append(match['gameId'])
        return

    def update_player_table_stats(self):
        print("Updating {}'s table data".format(self.account_name))

        for match in self.user_matches:

            session = orm.scoped_session(LolParser.sm)

            #row = db.select([self.user_table]).filter_by(match_id=match).fetchone()
            row = session.query(self.user_table).filter_by(match_id=match).first()
            champion = str(row.champion) # is this a string?

            match_data = LolParser.new_match_data[int(match)]

            for participant in match_data['participants']:
                participant_champ = str(participant['championId'])
                
                # if this participant is us, get some stats
                if participant_champ == champion:
                    kills = participant['stats']['kills']
                    deaths = participant['stats']['deaths']
                    assists = participant['stats']['assists']
                    wards_placed = participant['stats']['wardsPlaced']
                    damage_to_champs = participant['stats']['totalDamageDealtToChampions']
                    damage_to_turrets = participant['stats']['damageDealtToTurrets']
                    vision_wards_bought = participant['stats']['visionWardsBoughtInGame']
                    wards_killed = participant['stats']['wardsKilled']
                    
                    if 'firstBloodKill' in participant['stats']:
                        first_blood_kill = participant['stats']['firstBloodKill']
                    else:
                        first_blood_kill = 0
                        
                    if 'firstBloodAssist' in participant['stats']:
                        first_blood_assist = participant['stats']['firstBloodAssist']
                    else:
                        first_blood_assist = 0
                    
                    # can we make an object that has all the properties of the table
                    # set all the properties, then insert it with 1 passed argument (the object) 
                    # instead of doing this?

                    # update this match in the table
                    match_stats_insert = self.user_table.update().values( 
                            kills=kills,deaths=deaths,assists=assists,
                            wards_placed=wards_placed,damage_to_champs=damage_to_champs,
                            damage_to_turrets=damage_to_turrets,
                            vision_wards_bought=vision_wards_bought,
                            wards_killed=wards_killed).where(self.user_table.c.match_id == match)

                    results = LolParser.connection.execute(match_stats_insert)


                    # add champ name after adding champ table.
                    
                    

