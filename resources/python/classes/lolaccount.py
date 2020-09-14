""" lolaccount.py class

This class contains all the methods that are used for each individual account object
to be able to gather and store league of legends data into a database.

"""
import time
from typing import Tuple, Dict
import sqlalchemy as db
from sqlalchemy import and_
from .lolparser import LolParser
class LolAccount():
    """ Contains all the methods and functions needed to store the gathered data into the database

        Attributes:
            account_name  (str): the account name for our account
            game_index    (str): starting game index for matches API
            new_user_matches  (list: int): list of new matches to be added to the db for this player
            previous_player_matches (list: int): the list of games we currently have for this player
            account_id    (str): the account_id of this account from riot
            _match_types (list: int): Holds a list of all game modes we collect data for

    """
    _match_types = [400, 410, 420, 440, 700] # make sure this includes new types of matchmade games.
    def __init__(self, name):
        self.account_name = name
        self.new_user_matches = []
        self._game_index = 0
        self._account_id = LolParser.get_user_id(self.account_name)
        self._previous_player_matches = []

    def set_previous_player_matches(self):
        """ Stores the matches we currently have for this account into previous_player_matches

        """
        select_previous_matches  = db.select([LolParser.match_data_table]).where(\
            LolParser.match_data_table.c.player == self.account_name)

        player_match_history = LolParser.connection.execute(select_previous_matches).fetchall()

        for match in player_match_history:
            self._previous_player_matches.append(match.match_id)

    def set_new_user_matches(self):
        """ Stores the new match_ids we're getting data for into new_user_matches

        """
        self.set_previous_player_matches()

        while self._game_index < LolParser.max_game_index:

            time.sleep(.1)
            player_matches = LolParser.get_new_match_ids(\
                    self._account_id, self._game_index,self._game_index+100)

            if not player_matches['matches']:
                break

            for match in player_matches['matches']:
                if match['gameId'] not in self._previous_player_matches:
                    if match['queue'] in self._match_types:
                        match_sql_insert = db.insert(LolParser.match_data_table).values(\
                                match_id=match['gameId'],\
                                player=self.account_name,\
                                champion=match['champion'])

                        LolParser.connection.execute(match_sql_insert)
                        self.new_user_matches.append(match['gameId'])

            self._game_index += 100

    # Gets all the stats for a single player/match and puts them into the table.
    def update_player_table_stats(self):
        """ Goes through new_user_matches and updates match_data table for each match_id

        """
        LolParser.logger.info("Updating %s's match data", self.account_name)

        for match in self.new_user_matches:
            select_new_match_row = db.select([LolParser.match_data_table]).where(\
                    and_(LolParser.match_data_table.c.match_id==match,\
                    LolParser.match_data_table.c.player==self.account_name))

            new_match_row = LolParser.connection.execute(select_new_match_row).fetchone()
            champion = new_match_row.champion

            match_data = LolParser.new_match_data[match]

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
                    gold_per_minute, creeps_per_minute, xp_per_minute = \
                           LolAccount.get_gold_cs_xp_delta(timeline)

                    if role != "NONE":
                        enemy_champ = self.get_enemy_champ(role, champion,\
                                match_data['participants'])
                        if enemy_champ != -1:
                            enemy_champ_name = self.get_champ_name(enemy_champ)
                        else:
                            enemy_champ_name = None
                    else:
                        enemy_champ = None
                        enemy_champ_name = None

                    champ_items = self.get_items(participant['stats'])
                    champ_perks = self.get_perks(participant['stats'])

                    match_stats_insert = LolParser.match_data_table.update().values(
                            kills=kills,\
                            deaths=deaths,\
                            assists=assists,\
                            role=role,\
                            wards_placed=wards_placed,\
                            damage_to_champs=damage_to_champs,\
                            damage_to_turrets=damage_to_turrets,\
                            vision_wards_bought=vision_wards_bought,\
                            gold_per_minute=gold_per_minute,\
                            creeps_per_minute=creeps_per_minute,\
                            xp_per_minute=xp_per_minute,\
                            champion_name=champ_name,\
                            enemy_champion=enemy_champ,\
                            enemy_champion_name=enemy_champ_name,\
                            first_blood=first_blood_kill,\
                            first_blood_assist=first_blood_assist,\
                            items=champ_items,\
                            perks=champ_perks,\
                            wards_killed=wards_killed).where(\
                                and_(LolParser.match_data_table.c.match_id == match,\
                                        LolParser.match_data_table.c.player == self.account_name))

                    LolParser.connection.execute(match_stats_insert)
                    break # gets us outta the loop as soon as we put our data in.

    def update_team_data_table(self):
        LolParser.logger.info("Adding %s's new matches to the team_data table.", self.account_name)
        previous_matches = []

        select_existing_matches  = db.select([LolParser.team_data_table])

        existing_match_history = LolParser.connection.execute(select_existing_matches).fetchall()

        for match in existing_match_history:
            previous_matches.append(match.match_id)

        for match in self.new_user_matches:
            if match not in previous_matches:
                # get this matches data from the big collection.
                match_data = LolParser.new_match_data[match]

                team_data, enemy_team_data, team_id = self.get_team_data(match, match_data)

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

                LolParser.connection.execute(team_data_table_insert)
            else:
                # This match was already in the table, but another one of our players
                # was in this game, so we need to add them to participants.
                select_existing_team_data_row = db.select([LolParser.team_data_table])\
                        .where(LolParser.team_data_table.c.match_id==match)

                existing_team_data_row = LolParser.connection.execute(\
                        select_existing_team_data_row).fetchone()

                current_participants = existing_team_data_row.participants
                match_participants_update = LolParser.team_data_table.update().values(\
                        participants=f"{current_participants}, {self.account_name}")\
                        .where(LolParser.team_data_table.c.match_id==match)

                LolParser.connection.execute(match_participants_update)

    @staticmethod
    def get_gold_cs_xp_delta(timeline):
        num_of_deltas = 0
        total_gold = 0
        total_creeps = 0
        total_xp = 0
        cspm = 0
        gpm = 0
        xppm = 0

        try:
            for delta in timeline['goldPerMinDeltas'].items():
                total_gold += delta[1]
                num_of_deltas += 1

            gpm = float(total_gold / num_of_deltas)

            # what are the values of deltas here?
            for delta in timeline['creepsPerMinDeltas'].items():
                total_creeps += delta[1]

            cspm = float(total_creeps / num_of_deltas)

            for delta in timeline['xpPerMinDeltas'].items():
                total_xp += delta[1]

            xppm = float(total_xp / num_of_deltas)
        except ZeroDivisionError:
            LolParser.logger.warning("NO gold per minute or creeps per minute deltas, GTFO")

        return gpm, cspm, xppm

    @staticmethod
    def get_role(timeline):
        lane = timeline['lane']
        role = timeline['role']

        if lane == 'BOTTOM':
            if role == 'DUO_SUPPORT':
                return 'SUPPORT'
            if role == 'DUO_CARRY':
                return  'BOTTOM'

            return  'NONE'

        if role == "SOLO" and lane not in ('TOP', 'MIDDLE', 'JUNGLE'):
            return 'NONE'

        return lane


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

        if 'NONE' in enemy_participants_roles:
            return 0

        # if enemy_participants_roles has 5 unique values, we're good.
        if 'TOP' in enemy_participants_roles and 'MIDDLE' in enemy_participants_roles \
                and 'JUNGLE' in enemy_participants_roles and 'BOTTOM' in enemy_participants_roles\
                and 'SUPPORT' in enemy_participants_roles:

            #get the index of the role we passed in, and pass that champion back.
            return enemy_champions[enemy_participants_roles.index(role)]

        return 0

    @staticmethod
    def get_start_time_and_duration(match):
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

    @staticmethod
    def get_champ_name(champ_id):

        select_champion_row = db.select([LolParser.champs_table]).where(\
                LolParser.champs_table.c.key==champ_id)

        champion_row = LolParser.connection.execute(select_champion_row).fetchone()

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

    @staticmethod
    def get_items(participant_stats):
        champ_items = ""
        items = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        for item in items:
            if item:

                select_items_row = db.select([LolParser.items_table]).where(\
                        LolParser.items_table.c.key==participant_stats[item])

                items_row = LolParser.connection.execute(select_items_row).fetchone()
                if items_row:
                    champ_items += "{}, ".format(items_row.name)
                else:
                    champ_items += "NOT FOUND, " # I may eventually only return slots with items

        champ_items = champ_items[:-2]
        return champ_items

    @staticmethod
    def get_perks(participant_stats: Dict) -> list:
        """ This function gets the perk name from the perks table Note: This isn't implemented yet

            Args:
                participant_stats: A dict from riot games containing stats info

            Returns:
                A list of perk names from the database
        """
        champ_perks = ""
        perks = ['perk0', 'perk1', 'perk2', 'perk3', 'perk4', 'perk5']
        for perk in perks:
            if perk:
                champ_perks += f"{participant_stats[perk]}, "

        champ_perks = champ_perks[:-2]
        return champ_perks

    def get_team_data(self, match: int, match_data: Dict) -> Tuple[Dict, Dict, int]:
        """ Returns Team data for both teams, as well as the team_id for both teams

            Args:
                match: the match_id we use to query the db with
                match_data: A dict containing lots of data about our match

            Returns:
                team_data: our teams data from this match
                enemy_team-data: enemy teams data from this match
                team_id: our teams team_id
        """

        select_match_data_row = db.select([LolParser.match_data_table]).where(\
                and_(LolParser.match_data_table.c.match_id==match,\
            LolParser.match_data_table.c.player==self.account_name))

        match_data_row = LolParser.connection.execute(select_match_data_row).fetchone()

        champion = match_data_row.champion

        for participant in match_data['participants']:
            participant_champ = participant['championId']
            if participant_champ == champion:
                team_id = participant['teamId']
                if team_id == 100:
                    team_data = match_data['teams'][0]
                    enemy_team_data = match_data['teams'][1]
                    #enemy_team_id = 200
                elif team_id == 200:
                    team_data = match_data['teams'][1]
                    enemy_team_data = match_data['teams'][0]
                    #enemy_team_id = 100

                break

        return team_data, enemy_team_data, team_id
