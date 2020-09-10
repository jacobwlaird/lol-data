import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
import time
from sqlalchemy import orm, and_
from .lolparser import LolParser
import logging

class LolAccount(object):
    def __init__(self, name):
        self.account_name = name
        self.game_index = 0
        self.user_matches = []
        self.previous_player_matches = []

        self.account_id = '' #This is needed to get our matches later.

        logging.basicConfig(filename=LolParser.log_file_name,level=logging.DEBUG)

    #This saves the users previous matches, and new matches to be added.
    def get_user_matches(self):
        while self.game_index < LolParser.max_game_index:
            self.add_user_match_history(self.game_index, self.game_index+100)  #these should be 100
            if not self.user_matches:
                break

            self.game_index += 100


    def set_user_id(self):
        # this will call the api once, to get our account id, so we dont double call it.
        try:
            account_response = requests.get(''.join([LolParser.base_summoner_url, LolParser.account_name_url, self.account_name, "?api_key=", LolParser.api_key]))
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            self.account_id = account_data['accountId']
        except Exception as e:
            if e.response.status_code == 403:
                logging.critical("Api key is probably expired")

            logging.critical("set_user_id broke")


    # sets the previous_matches and new_player_matches properties.
    def add_user_match_history(self, start_index=0, end_index=100):
        # This has to only select the current loop users matches.
        player_matches = LolParser.get_account_info(self.account_name, self.account_id, start_index, end_index)
        select_previous_matches = "SELECT match_id FROM match_data WHERE player = '{}';".format(self.account_name, self.account_name)
        player_match_history = pd.read_sql(select_previous_matches, LolParser.connection)

        for match in player_match_history['match_id']:
            self.previous_player_matches.append(match)

        if not 'matches' in player_matches.keys():
            return

        for match in player_matches['matches']:
            if match['gameId'] not in self.previous_player_matches and match['gameId'] > 200000000:
                if match['queue'] in LolParser.match_types:
                    match_sql_insert = db.insert(LolParser.match_data_table).values(match_id=match['gameId'], 
                            player=self.account_name,
                            champion=match['champion'])

                    results = LolParser.connection.execute(match_sql_insert)
                    self.user_matches.append(match['gameId'])
        return

    # Gets all the stats for a single player/match and puts them into the table.
    def update_player_table_stats(self):
        logging.info("Updating {}'s match data".format(self.account_name))

        for match in self.user_matches:
            session = orm.scoped_session(LolParser.sm)
            # this also has to filter by player name?
            row = session.query(LolParser.match_data_table).filter(and_(LolParser.match_data_table.c.match_id==match, 
                LolParser.match_data_table.c.player==self.account_name)).first()
            session.close()

            champion = row.champion

            match_data = LolParser.new_match_data[int(match)]

            for participant in match_data['participants']:
                participant_champ = participant['championId']
                
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
                    champ_name = self.get_champ_name(champion)
                    
                    if 'firstBloodKill' in participant['stats']:
                        first_blood_kill = participant['stats']['firstBloodKill']
                    else:
                        first_blood_kill = 0
                        
                    if 'firstBloodAssist' in participant['stats']:
                        first_blood_assist = participant['stats']['firstBloodAssist']
                    else:
                        first_blood_assist = 0

                    timeline = participant['timeline']

                    role = self.get_role(timeline)
                    gold_per_minute, creeps_per_minute, xp_per_minute = self.get_gold_cs_xp_delta(timeline)

                    if role != "NONE":
                        enemy_champ = self.get_enemy_champ(role, champion, match_data['participants'])
                        if enemy_champ != None:
                            enemy_champ_name = self.get_champ_name(enemy_champ)
                        else:
                            enemy_champ_name = None
                    else:
                        enemy_champ = None 
                        enemy_champ_name = None
                    
                    champ_items = self.get_items(participant['stats'])
                    champ_perks = self.get_perks(participant['stats'])

                    #match_stats_insert = self.user_table.update().values( 
                    match_stats_insert = LolParser.match_data_table.update().values( 
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
                            xp_per_minute=xp_per_minute,
                            champion_name=champ_name,
                            enemy_champion=enemy_champ,
                            enemy_champion_name=enemy_champ_name,
                            first_blood=first_blood_kill,
                            first_blood_assist=first_blood_assist,
                            items=champ_items,
                            perks=champ_perks,
                            wards_killed=wards_killed).where(
                                and_(LolParser.match_data_table.c.match_id == match, LolParser.match_data_table.c.player == self.account_name))

                    results = LolParser.connection.execute(match_stats_insert)
                    break # gets us outta the loop as soon as we put our data in.
                    
    def update_team_data_table(self):
       logging.info("Adding {}'s new matches to the team_data table.".format(self.account_name))
       previous_matches = [] # this needs to changed to be better, but for some reason my match not in exisiting matches condition isn't working.

       select_existing_matches = "SELECT match_id FROM team_data;"
       existing_match_history = pd.read_sql(select_existing_matches, LolParser.connection)
       for match in existing_match_history['match_id']:   
            previous_matches.append(match)

       for match in self.user_matches:
            if match not in previous_matches:
                # get this matches data from the big collection.
                match_data = LolParser.new_match_data[int(match)]
                 
                team_data, enemy_team_data, team_id, enemy_id = self.get_team_data(match, match_data)

                # get some team information.
                game_outcome = team_data['win']
                first_blood = team_data['firstBlood']
                first_baron = team_data['firstBaron']
                first_tower = team_data['firstTower']
                first_rift_herald = team_data['firstRiftHerald']
                ally_rift_herald_kills = team_data['riftHeraldKills']
                first_dragon = team_data['firstDragon']
                ally_dragon_kills = team_data['dragonKills']
                first_inhib = team_data['firstInhibitor']
                inhib_kills = team_data['inhibitorKills']
                list_of_bans = ""
                list_of_enemy_bans = ""
                game_version = match_data['gameVersion']

                # sometimes we need enemy info too.
                enemy_dragon_kills = enemy_team_data['dragonKills']
                enemy_rift_herald_kills = enemy_team_data['riftHeraldKills']

                #these could pass in only bans, not the whole object.
                list_of_bans = self.get_team_bans(team_data)
                list_of_enemy_bans = self.get_team_bans(enemy_team_data)

                allies, enemies = self.get_allies_and_enemies(team_id, match)
                start_time, duration = self.get_start_time_and_duration(match) 

                team_data_table_insert = db.insert(LolParser.team_data_table).values(match_id=match, 
                        participants=self.account_name,
                        win=game_outcome,
                        first_blood=first_blood,
                        first_baron=first_baron,
                        first_tower=first_tower,
                        first_rift_herald=first_rift_herald,
                        ally_rift_herald_kills=ally_rift_herald_kills,
                        first_dragon=first_dragon,
                        ally_dragon_kills=ally_dragon_kills,
                        first_inhib=first_inhib,
                        inhib_kills=inhib_kills,
                        bans=list_of_bans,
                        enemy_bans=list_of_enemy_bans,
                        game_version=game_version,
                        allies=allies,
                        enemies=enemies,
                        start_time=start_time,
                        enemy_rift_herald_kills=enemy_rift_herald_kills,
                        enemy_dragon_kills=enemy_dragon_kills,
                        duration=duration
                        )

                results = LolParser.connection.execute(team_data_table_insert)
            else:
                # This match was already in the table, but another one of our players was in this game, so we need to add them to participants.
                session = orm.scoped_session(LolParser.sm)
                row = session.query(LolParser.team_data_table).filter_by(match_id=match).first()
                session.close()

                current_participants = row.participants
                match_participants_update = LolParser.team_data_table.update().values( 
                        participants="{}, {}".format(current_participants, self.account_name)).where(LolParser.team_data_table.c.match_id == match)

                results = LolParser.connection.execute(match_participants_update)

    def get_gold_cs_xp_delta(self, timeline):
        num_of_deltas = 0
        total_gold = 0
        total_creeps = 0
        total_xp = 0
        cspm = 0
        gpm = 0
        xppm = 0
        
        try:
            for deltas, value in timeline['goldPerMinDeltas'].items():
                total_gold += value
                num_of_deltas += 1

            gpm = float(total_gold / num_of_deltas)

            for deltas, value in timeline['creepsPerMinDeltas'].items():
                total_creeps += value

            cspm = float(total_creeps / num_of_deltas)

            for deltas, value in timeline['xpPerMinDeltas'].items():
                total_xp += value
                num_of_deltas += 1

            xppm = float(total_xp / num_of_deltas)
        except Exception as e:
            logging.warning("NO gold per minute or creeps per minute deltas, GTFO")

        return gpm, cspm, xppm

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

    def get_enemy_champ(self, role, champion, participants):
        enemy_participants_roles = []
        enemy_champions = []

        for participant in participants:
            participant_champ = participant['championId']

            # If the participant is us, then grab our team.
            if participant_champ == champion:
                our_team_id = participant['teamId']
                break

        
        for participant in participants:
            if participant['teamId'] != our_team_id:
                timeline = participant['timeline']
                enemy_participants_roles.append(self.get_role(timeline))
                enemy_champions.append(participant['championId'])

        # if enemy_participants_roles has 5 unique values, we're good.
        if 'NONE' in enemy_participants_roles:
            return None

        if 'TOP' in enemy_participants_roles and 'MIDDLE' in enemy_participants_roles and 'JUNGLE' in enemy_participants_roles \
                and 'BOTTOM' in enemy_participants_roles and 'SUPPORT' in enemy_participants_roles:

            #get the index of the role we passed in, and pass that champion back.
            return enemy_champions[enemy_participants_roles.index(role)]
        else:
            return None

    def get_start_time_and_duration(self, match):
        match_data = LolParser.new_match_data[int(match)]
        
        start_t = match_data['gameCreation']

        # Creation includes miliseconds which we don't care about.
        start_t = start_t / 1000
        start_t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_t))
        
        # Duration might go over an hour, so I have to use a check for presentability's sake
        duration = match_data['gameDuration']
        if duration > 3600:
            duration = time.strftime("%H:%M:%S", time.gmtime(duration))
        else:
            duration = time.strftime("%M:%S", time.gmtime(duration))
        
        return start_t, duration

    def get_champ_name(self, champ_id):
        session = orm.scoped_session(LolParser.sm)
        champion_row = session.query(LolParser.champs_table).filter_by(key=champ_id).first()
        session.close()
        return champion_row.name

    def get_allies_and_enemies(self, team_id, match):
        match_data = LolParser.new_match_data[int(match)]

        allies = ""
        enemies = ""
        for participant in match_data['participants']:
            if participant['teamId'] == team_id:
                allies += "{}, ".format(self.get_champ_name(participant['championId']))
            else:
                enemies += "{}, ".format(self.get_champ_name(participant['championId']))

        allies = allies[:-2]
        enemies = enemies[:-2]

        return allies, enemies

    def get_team_bans(self, team_data):
        list_of_bans = ""

        for ban in team_data['bans']:
            list_of_bans += "{}, ".format(self.get_champ_name(ban['championId']))

        list_of_bans = list_of_bans[:-2] # removes the last two characters
        return list_of_bans

    def get_items(self, participant_stats):
        champ_items = ""
        items = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        for item in items:
            if item:
                # here we need to ping our itmes table and get the actual name of the item
                session = orm.scoped_session(LolParser.sm)
                row = session.query(LolParser.items_table).filter_by(key=participant_stats[item]).first()
                session.close()

                if row:
                    champ_items += "{}, ".format(row.name)
                else:
                    champ_items += "NOT FOUND, "

        champ_items = champ_items[:-2]
        return champ_items

    # getting the perk name from the db is on hold until I can figure out how to populate the db.
    def get_perks(self, participant_stats):
        champ_perks = ""
        perks = ['perk0', 'perk1', 'perk2', 'perk3', 'perk4', 'perk5']
        for perk in perks:
            if perk:
               #session = orm.scoped_session(LolParser.sm)
                #row = session.query(LolParser.items_table).filter_by(key=item).first()
                #session.close()
                champ_perks += "{}, ".format(participant_stats[perk])

                #if row:
                #    champ_perks = "{}, ".format(row.name)
                #else:
                #    champ_items += "NOT FOUND, "

        champ_perks = champ_perks[:-2]
        return champ_perks

    def get_team_data(self, match, match_data):
        session = orm.scoped_session(LolParser.sm)
        row = session.query(LolParser.match_data_table).filter(and_(LolParser.match_data_table.c.match_id==match, 
            LolParser.match_data_table.c.player==self.account_name)).first()

        session.close()

        champion = row.champion
        for participant in match_data['participants']:
            participant_champ = participant['championId']
            if participant_champ == champion:
                team_id = participant['teamId']
                if team_id == 100:
                    team_data = match_data['teams'][0]
                    enemy_team_data = match_data['teams'][1]
                    enemy_team_id = 200
                    break
                elif team_id == 200:
                    team_data = match_data['teams'][1]
                    enemy_team_data = match_data['teams'][0]
                    enemy_team_id = 100
                    break

        return team_data, enemy_team_data, team_id, enemy_team_id
