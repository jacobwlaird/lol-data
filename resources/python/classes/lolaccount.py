""" lolaccount.py class

This class contains all the methods that are used for each individual account object
to be able to gather and store league of legends data into a database.

"""
import time
from typing import Tuple, Dict
import sqlalchemy as db # type: ignore
from sqlalchemy import and_
from .lolparser import LolParser
class LolAccount():
    """ Contains all the methods and functions needed to store the gathered data into the database

        Attributes:
            account_name  (str): the account name for our account
            game_index    (str): starting game index for matches API
            new_user_matches  (list: int): list of new matches to be added to the db for this player
            previous_player_matches (list: int): the list of games we currently have for this player
            _account_id    (str): the account_id of this account from riot
            _match_types   (list: int): Holds a list of all game modes we collect data for

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

            if not player_matches['matches']: # this is busted?
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

    def update_player_table_stats(self):
        """ Goes through new_user_matches and updates match_data table for each match_id

        """
        LolParser.logger.info("Updating %s's match data", self.account_name)

        for match in self.new_user_matches:
            match_data = LolParser.new_match_data[match]

            participant_index = self.get_participant_index(match_data['participantIdentities'])

            participant = match_data['participants'][participant_index]
            stats = participant['stats']

            kills = stats['kills']
            deaths = stats['deaths']
            assists = stats['assists']
            wards_placed = stats['wardsPlaced']
            damage_to_champs = stats['totalDamageDealtToChampions']
            damage_to_turrets = stats['damageDealtToTurrets']
            vision_wards_bought = stats['visionWardsBoughtInGame']
            wards_killed = stats['wardsKilled']

            champ_name = self.get_champ_name(participant['championId'])

            first_blood_kill, first_blood_assist = LolAccount.get_first_blood_kill_assist(stats)
            timeline = participant['timeline']

            role = self.get_role(timeline)
            gold_per_minute, creeps_per_minute, xp_per_minute = \
                   LolAccount.get_gold_cs_xp_delta(timeline)

            enemy_champ = self.get_enemy_champ(role, participant_index, match_data['participants'])
            enemy_champ_name = self.get_champ_name(enemy_champ)

            champ_items = self.get_items(stats)
            champ_perks = self.get_perks(stats)

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

    def update_team_data_table(self):
        """ Goes through new_user_matches and updates team_data table for each match_id

        """
        LolParser.logger.info("Adding %s's new matches to the team_data table.", self.account_name)

        previous_matches = LolAccount.get_previous_matches()

        for match in self.new_user_matches:
            if match not in previous_matches:

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

                list_of_bans = self.get_team_bans(team_data['bans'])
                list_of_enemy_bans = self.get_team_bans(enemy_team_data['bans'])

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
    def get_gold_cs_xp_delta(timeline: dict) -> Tuple[float, float, float]:
        """ Gets the gold, cs, and xp deltas from a timeline

            Args:
                timeline: a timeline object associated with a participant in a match

            Returns:
                A tuple containing the gold, cs, and xp deltas

        """
        num_of_deltas = 0
        total_gold = 0
        total_creeps = 0
        total_xp = 0
        cspm = 0.0
        gpm = 0.0
        xppm = 0.0

        try:
            for delta in timeline['goldPerMinDeltas'].items():
                total_gold += delta[1]
                num_of_deltas += 1

            gpm = float(total_gold / num_of_deltas)

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
    def get_role(timeline: dict) -> str:
        """ Gets a players role based on their timeline

            Args:
                timeline: a timeline object associated with a participant in a match

            Returns:
                The lane the player played in, or NONE if we couldn't determine.

        """
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


    def get_enemy_champ(self, role: str, participant_index: int, participants: dict) -> int:
        """ Gets our players enemy champion id, if the enemy team has all 5 roles.

            Args:
                role: a string denoting our role. TOP, JUNGLE, BOTTOM, etc.
                participant_index: the index of our participant dict
                participants: A large dictionary of the games participants, whos keys are ints

            Returns:
                An integer value representing the champion that was played by our lane opponent

        """
        if role != 'NONE':
            enemy_participants_roles = []
            enemy_champions = []
            our_team_id = participants[participant_index]['teamId']

            for participant in participants:
                if participant['teamId'] != our_team_id:
                    timeline = participant['timeline']
                    enemy_participants_roles.append(self.get_role(timeline))
                    enemy_champions.append(participant['championId'])

            if 'NONE' in enemy_participants_roles:
                return -1

            if 'TOP' in enemy_participants_roles and 'MIDDLE' in enemy_participants_roles \
                    and 'JUNGLE' in enemy_participants_roles and 'BOTTOM' in\
                    enemy_participants_roles and 'SUPPORT' in enemy_participants_roles:

                #get the index of the role we passed in, and pass that champion back.
                return enemy_champions[enemy_participants_roles.index(role)]

        return -1

    @staticmethod
    def get_start_time_and_duration(match: int) -> Tuple:
        """ Gets the start time and duration of an individual match

            Args:
                match: an integer match_id used to access the new_match_data dict

            Returns:
                A Tuple containing the start_time and duration converted from MS
        """
        match_data = LolParser.new_match_data[match]

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
    def get_champ_name(champ_id: int) -> str:
        """ Gets the champ name from the champions table using their champ_id

            Args:
                champ_id: The integer value of the champion we're getting the name of

            Returns:
                The champions name, or None, if the passed champ_id was -1 (no champ)

        """
        select_champion_row = db.select([LolParser.champs_table]).where(\
                LolParser.champs_table.c.key==champ_id)

        champion_row = LolParser.connection.execute(select_champion_row).fetchone()
        if champion_row.key != -1:
            return champion_row.name

        return "None"

    def get_allies_and_enemies(self, team_id: int, match: int) -> Tuple[str, str]:
        """ Creates a list of allied and enemy champs played in a particular match.

            Args:
                team_id: An integer denoting what team we were on (100 or 200)
                match: the match_id for this particular match

            Returns:
                A tuple containing all of the allied and enemy champions.

        """
        match_data = LolParser.new_match_data[match]

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

    def get_team_bans(self, bans: list) -> str:
        """ Builds a list of a teams banned champions using that teams ban list

            Args:
                bans: a list containing ban dicts

            Returns:
                A string containing all of the banned champions for a team
        """
        list_of_bans = ""

        for ban in bans:
            list_of_bans += "{}, ".format(self.get_champ_name(ban['championId']))

        list_of_bans = list_of_bans[:-2]
        return list_of_bans

    @staticmethod
    def get_items(participant_stats: dict) -> str:
        """ Builds a string containing all of the items purchased by a participant

            Args:
                participant_stats: a dictionary containing all of a participants stats

            Returns:
                A string of item names
        """
        champ_items = ""
        items = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        for item in items:
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
    def get_perks(participant_stats: dict) -> str:
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

    def get_team_data(self, match: int, match_data: dict) -> Tuple[Dict, Dict, int]:
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

    def get_participant_index(self, participant_identities: dict) -> int:
        """ Gets a participants index based on their account_id

            Args:
                participant_identities: a dictionary containing all 10 players identities

            Returns:
                The index of our accounts participant

        """
        for index, player in enumerate(participant_identities):
            if player['player']['accountId'] == self._account_id:
                return index

        return -1

    @staticmethod
    def get_first_blood_kill_assist(stats: dict) -> Tuple[int, int]:
        """ Returns integers denoting if a participant was involved in a first blood
            Args:
                stats: a large dictionary object containing a ton of stats

            Returns:
                Two integers denoting if this participant was (1) or was not (0) part of fb

        """

        if 'firstBloodKill' in stats:
            first_blood_kill = stats['firstBloodKill']
        else:
            first_blood_kill = 0

        if 'firstBloodAssist' in stats:
            first_blood_assist = stats['firstBloodAssist']
        else:
            first_blood_assist = 0

        return first_blood_kill, first_blood_assist

    @staticmethod
    def get_previous_matches() -> list:
        """ Creates and returns a list of existing matches that we have stored in team_data

        """
        previous_matches = []
        select_existing_matches = db.select([LolParser.team_data_table])

        existing_match_history = LolParser.connection.execute(select_existing_matches).fetchall()

        for match in existing_match_history:
            previous_matches.append(match.match_id)

        return previous_matches
