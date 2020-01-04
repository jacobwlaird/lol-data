import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
import time
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
            self.add_user_match_history(self.game_index, self.game_index+10) 
            if not self.user_matches:
                break

            self.game_index += 10

    # sets the previous_matches and new_player_matches properties.
    def add_user_match_history(self, start_index=0, end_index=100):
        player_matches = LolParser.get_account_info(self.account_name, start_index, end_index)
        select_previous_matches = "SELECT match_id FROM {}_match_history;".format(self.account_name)
        player_match_history = pd.read_sql(select_previous_matches, LolParser.connection)

        for match in player_match_history['match_id']:
            self.previous_player_matches.append(match)

        # could maybe improve this by just selecting games that are in user table but not in matches
        for match in player_matches['matches']:
            if match['gameId'] not in self.previous_player_matches and match['gameId'] > 200000000:
                if match['queue'] in LolParser.match_types:
                    match_sql_insert = db.insert(self.user_table).values(match_id=match['gameId'], champion=match['champion'])

                    results = LolParser.connection.execute(match_sql_insert)
                    self.user_matches.append(match['gameId'])
        return

    # Gets all the stats and puts them into the table.
    def update_player_table_stats(self):
        print("Updating {}'s table data".format(self.account_name))

        for match in self.user_matches:
            session = orm.scoped_session(LolParser.sm)

            row = session.query(self.user_table).filter_by(match_id=match).first()
            champion = str(row.champion)

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

                    # some calculated stats

                    timeline = participant['timeline']

                    role = self.get_role(timeline)
                    gold_per_minute, creeps_per_minute = self.get_gold_cs_delta(timeline)

                    if role != "NONE":
                        enemy_champ = self.get_enemy_champ(role, champion, match_data['participants'])
                        enemy_champ_name = 'COMING SOON'
                    else:
                        enemy_champ = None # what can we do about this?
                        enemy_champ_name = 'NONE'
                    
                    # can we make an object that has all the properties of the table
                    # set all the properties, then insert it with 1 passed argument (the object) 
                    # instead of doing this? yes, when we move to orm.

                    # update this match in the table
                    match_stats_insert = self.user_table.update().values( 
                            kills=kills,
                            deaths=deaths,
                            assists=assists,
                            role=role,
                            wards_placed=wards_placed,
                            damage_to_champs=damage_to_champs,
                            damage_to_turrets=damage_to_turrets,
                            vision_wards_bought=vision_wards_bought,
                            gold_per_minute=gold_per_minute,
                            creeps_per_minute=creeps_per_minute,
                            enemy_champion=enemy_champ,
                            enemy_champion_name=enemy_champ_name,
                            wards_killed=wards_killed).where(self.user_table.c.match_id == match)

                    results = LolParser.connection.execute(match_stats_insert)
                    break # gets us outta the loop as soon as we put our data in.
                    
    def get_gold_cs_delta(self, timeline):
        num_of_deltas = 0
        total_gold = 0
        total_creeps = 0
        cspm = 0
        gpm = 0
        
        try:
            for deltas, value in timeline['goldPerMinDeltas'].items():
                total_gold += value
                num_of_deltas += 1

            gpm = float(total_gold / num_of_deltas)

            for deltas, value in timeline['creepsPerMinDeltas'].items():
                total_creeps += value

            cspm = float(total_creeps / num_of_deltas)
        except Exception as e:
            print("NO gold per minute or creeps per minute deltas, GTFO")

        return gpm, cspm

    def get_role(self, timeline): 
        lane = timeline['lane']
        role = timeline['role']

        if lane == 'BOT' or lane == 'BOTTOM':
            if role == 'DUO_SUPPORT':
                return 'SUPPORT'
            elif role == 'DUO_CARRY':
                return  'BOTTOM'
            else:
                return  'NONE'

        if role == "SOLO" and (lane != 'TOP' and lane != 'MID' and lane != 'MIDDLE' and lane != 'JUNGLE'):
            return 'NONE'
        else:
            return lane

        if role == 'MID':
            return 'MIDDLE'


    # we also need our champion, and the data itself
    def get_enemy_champ(self, role, champion, participants):
        # I think we'll first, determine which team we're on. Then run get_role for every enemy
        # if we have 5 different roles on the opponent team, and no NONE, then we can pick our enemy champ.
        enemy_participants_roles = []
        enemy_champions = []

        for participant in participants:
            participant_champ = str(participant['championId'])

            # If the participant is us, then grab our team.
            if participant_champ == champion:
                our_team_id = participant['teamId']
                break

        
        for participant in participants:
            if participant['teamId'] != our_team_id:
                timeline = participant['timeline']
                enemy_participants_roles.append(self.get_role(timeline))
                enemy_champions.append(participant['championId'])

        print(enemy_participants_roles)
        # if enemy_participants_roles has 5 unique values, we're good.
        if 'NONE' in enemy_participants_roles:
            return None

        if 'TOP' in enemy_participants_roles and 'MIDDLE' in enemy_participants_roles and 'JUNGLE' in enemy_participants_roles \
                and 'BOTTOM' in enemy_participants_roles and 'SUPPORT' in enemy_participants_roles:

            #get the index of the role we passed in, and pass that champion back.
            print(enemy_champions)
            print(enemy_participants_roles)
            return enemy_champions[enemy_participants_roles.index(role)]
        else:
            return None

        
                









