""" lolparser.py class

This class contains all the methods needed to store and retrieve league of legends
data to or from a database. It handles all db transactions during the script run,
as well as handling logging.

"""
import logging
import time
from typing import Tuple, Dict
from datetime import datetime as date
import configparser
import sqlalchemy as db # type: ignore
from sqlalchemy import exc # type: ignore

class LolParser():
    """ Contains all the methods and functions needed by loldata.py and lolaccount.py
        Attributes:

            _config         (obj): ConfigParser object for reading config file

            db_host        (str): database host address from config file
            db_user        (str): database user from config file
            db_pw          (str): database user password from config file
            db_name        (str): database name from config file

            engine        (obj): Sqlalchemy engine object created with config file contents
            connection    (obj): Sqlalchemy connection object created from the sqla engine
            metadata      (obj): Database metadata object

            champs_table     (obj): Sqlalchemy Table object for the champions table
            match_data_table (obj): Sqlalchemy Table object for the match_data table
            team_data_table  (obj): Sqlalchemy Table object for the team_data table
            items_table      (obj): Sqlalchemy Table object for the items table
            json_data_table  (obj): Sqlalchemy Table object for the json_data table
            runs_table       (obj): Sqlalchemy Table object for the script_runs table

            log_file_name (str): Log file name pulled from config file
            logger        (obj): Log object that we call to, to log
    """
    _config = configparser.ConfigParser()
    _config.read('./resources/python/general.cfg')

    db_host = _config.get('DATABASE', 'db_id')
    db_user = _config.get('DATABASE', 'db_user')
    db_pw = _config.get('DATABASE', 'db_password')
    db_name = _config.get('DATABASE', 'db_name')

    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(db_user,\
            db_pw, db_host, db_name), pool_size=100, max_overflow=100)
    connection = engine.connect()
    metadata = db.MetaData()

    champs_table = db.Table('champions', metadata, autoload=True, autoload_with=engine)
    match_data_table = db.Table('match_data', metadata, autoload=True, autoload_with=engine)
    team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)
    items_table = db.Table('items', metadata, autoload=True, autoload_with=engine)
    json_data_table = db.Table('json_data', metadata, autoload=True, autoload_with=engine)
    runs_table = db.Table('script_runs', metadata, autoload=True, autoload_with=engine)

    log_file_name = _config.get('LOGGING', 'file_name')
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG)
    logger = logging.getLogger()

    @classmethod
    def select_previous_matches(cls, account_name: str) -> list:
        """ Gets the matches we already have in match_data and returns the match_ids in a list

            Args:
                account_name: the name of the player we're getting matches for

            Returns:
                A list of match_data row objects

        """

        select_previous_matches  = db.select([cls.match_data_table]).where(\
            cls.match_data_table.c.player == account_name)

        player_match_history = cls.connection.execute(select_previous_matches).fetchall()

        return player_match_history

    @classmethod
    def select_previous_team_data_matches(cls) -> list:
        """ Gets the matches we already have in team_data and returns a list of row objects

            Returns:
                A list of team_data row objects
        """
        select_previous_matches = db.select([cls.team_data_table])
        team_data_history = cls.connection.execute(select_previous_matches).fetchall()

        return team_data_history


    @classmethod
    def insert_player_table_data(cls, match_data: dict, account_name: str, account_id: str):
        """ updates parses through a match_data dict and update the table for a match_id

            Args:
                match_data: a large dict containing all the match data
                account_name: the player we're updating for
                account_id: the id of the player so we can determine participant index

        """

        participant_index = cls.get_participant_index(match_data['participantIdentities'],\
                account_id)

        match_id = match_data['gameId']
        player=account_name

        participant = match_data['participants'][participant_index]
        stats = participant['stats']
        champion = participant['championId']

        kills = stats['kills']
        deaths = stats['deaths']
        assists = stats['assists']
        wards_placed = stats['wardsPlaced']
        damage_to_champs = stats['totalDamageDealtToChampions']
        damage_to_turrets = stats['damageDealtToTurrets']
        vision_wards_bought = stats['visionWardsBoughtInGame']
        wards_killed = stats['wardsKilled']

        champ_name = cls.get_champ_name(participant['championId'])

        first_blood_kill, first_blood_assist = LolParser.get_first_blood_kill_assist(stats)
        timeline = participant['timeline']

        role = cls.get_role(timeline)
        gold_per_minute, creeps_per_minute, xp_per_minute = \
               cls.get_gold_cs_xp_delta(timeline)

        enemy_champ = cls.get_enemy_champ(role, participant_index, match_data['participants'])
        enemy_champ_name = cls.get_champ_name(enemy_champ)

        champ_items = cls.get_items(stats)
        champ_perks = LolParser.get_perks(stats)

        match_stats_insert = cls.match_data_table.insert().values(
                match_id=match_id,\
                player=player,\
                kills=kills,\
                deaths=deaths,\
                assists=assists,\
                role=role,\
                champion=champion,\
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
                wards_killed=wards_killed)

        cls.connection.execute(match_stats_insert)

    @classmethod
    def insert_team_data_table_row(cls, match_data: dict, account_name: str, account_id: str):
        """ Goes through a match_data dict, parses out information, and stores into team_data table

            Args:
                match_data: a large dict containing match data from riot api
                account_name: the name of the player we're storing games for
                account_id: the id of the player we're storing games for

        """

        team_data, enemy_team_data, team_id = cls.get_team_data(match_data, account_id)

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
        match = match_data['gameId']

        # sometimes we need enemy info too.
        enemy_dragon_kills = enemy_team_data['dragonKills']
        enemy_rift_herald_kills = enemy_team_data['riftHeraldKills']

        list_of_bans = cls.get_team_bans(team_data['bans'])
        list_of_enemy_bans = cls.get_team_bans(enemy_team_data['bans'])

        allies, enemies = cls.get_allies_and_enemies(team_id, match_data['participants'])
        start_time, duration = cls.get_start_time_and_duration(match_data['gameCreation'],\
                match_data['gameDuration'])

        team_data_table_insert = db.insert(cls.team_data_table).values(match_id=match,
                participants=account_name,
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

        cls.connection.execute(team_data_table_insert)

    @classmethod
    def update_team_data_table_row(cls, match: int, account_name: str):
        """ if the match we're trying to insert into team_data already exists, we update instead

            Args:
                match: the match_id we're updating
                account_name: the player we're updating the table for

        """
        select_existing_team_data_row = db.select([cls.team_data_table])\
                .where(cls.team_data_table.c.match_id==match)

        existing_team_data_row = cls.connection.execute(\
                select_existing_team_data_row).fetchone()

        current_participants = existing_team_data_row.participants
        match_participants_update = cls.team_data_table.update().values(\
                participants=f"{current_participants}, {account_name}")\
                .where(cls.team_data_table.c.match_id==match)

        cls.connection.execute(match_participants_update)

    @staticmethod
    def get_participant_index(participant_identities: dict, account_id: str) -> int:
        """ Gets a participants index based on their account_id

            Args:
                participant_identities: a dictionary containing all 10 players identities
                account_id: the account id of the player we're getting the index of

            Returns:
                The index of our accounts participant

        """
        for index, player in enumerate(participant_identities):
            if player['player']['accountId'] == account_id:
                return index

        return -1

    @classmethod
    def get_previous_matches(cls) -> list:
        """ Creates and returns a list of existing matches that we have stored in team_data

            Returns:
                A list of current match_ids stored in the team_data_table
        """
        previous_matches = []
        select_existing_matches = db.select([cls.team_data_table])

        existing_match_history = cls.connection.execute(select_existing_matches).fetchall()

        for match in existing_match_history:
            previous_matches.append(match.match_id)

        return previous_matches

    @classmethod
    def store_json_data(cls, match: int, json_formatted_string: str):
        """ Stores the json data into the json_data table

            Args:
                match: The match id we're storing data for
                json_formatted_string: The actual json data to be stored
        """

        try:
            json_sql_insert = db.insert(cls.json_data_table).values(match_id=match,\
                    json_data=json_formatted_string)

            cls.connection.execute(json_sql_insert)
        except exc.IntegrityError as e:
            cls.logger.warning("Could not store JSON. Maybe already stored?")
            cls.logger.warning(e)

    @classmethod
    def store_run_info(cls, source: str):
        """ Creates a new row in the script_runs table

            Args:
                source: The source of the script run (Daily, Manual, ManualWeb)
        """
        time_started = date.now().strftime("%Y-%m-%d %H:%M:%S")
        runs_sql_insert = db.insert(cls.runs_table).values(source=source,\
                start_time=time_started,\
                status="Running")

        cls.connection.execute(runs_sql_insert)

    @classmethod
    def update_run_info(cls, status: str, matches: str, message: str):
        """ Updates the currently running row in script_runs

            Args:
                status:  The status of the run (Failed, Success)
                matches: A string containing all the matches that were added by this script run
                message: Any message explaining the status of the run (exception if failed, etc)
        """
        time_ended = date.now().strftime("%Y-%m-%d %H:%M:%S")
        runs_sql_update = db.update(cls.runs_table).values(status=status,\
                matches_added=matches,\
                end_time=time_ended,\
                message=message).where(cls.runs_table.c.status == "Running")

        cls.connection.execute(runs_sql_update)

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

        cspm = -1.0
        gpm = -1.0
        xppm = -1.0

        if 'goldPerMinDeltas' in timeline and 'creepsPerMinDeltas' in timeline\
                and 'xpPerMinDeltas' in timeline:

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


    @classmethod
    def get_enemy_champ(cls, role: str, participant_index: int, participants: dict) -> int:
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
                    enemy_participants_roles.append(cls.get_role(timeline))
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
    def get_start_time_and_duration(game_create_time: float, game_duration: float) -> Tuple:
        """ Gets the start time and duration of an individual match

            Args:
                game_create_time: a float value of the game creation time
                game_duration: a float value of the game duration

            Returns:
                A Tuple containing the start_time and duration converted from MS
        """
        start_t = game_create_time

        # Creation includes miliseconds which we don't care about.
        start_t = start_t / 1000
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_t))

        # Duration might go over an hour, so I have to use a check for presentability's sake
        if game_duration > 3600:
            duration = time.strftime("%H:%M:%S", time.gmtime(game_duration))
        else:
            duration = time.strftime("%M:%S", time.gmtime(game_duration))

        return start_time, duration

    @classmethod
    def get_champ_name(cls, champ_id: int) -> str:
        """ Gets the champ name from the champions table using their champ_id

            Args:
                champ_id: The integer value of the champion we're getting the name of

            Returns:
                The champions name, or None, if the passed champ_id was -1 (no champ)

        """
        select_champion_row = db.select([cls.champs_table]).where(\
                cls.champs_table.c.key==champ_id)

        champion_row = cls.connection.execute(select_champion_row).fetchone()
        if champion_row.key != -1:
            return champion_row.name

        return "None"

    @classmethod
    def get_allies_and_enemies(cls, team_id: int, participants: list) -> Tuple[str, str]:
        """ Creates a list of allied and enemy champs played in a particular match.

            Args:
                team_id: An integer denoting what team we were on (100 or 200)
                participants: A list of participant objects from riot api

            Returns:
                A tuple containing all of the allied and enemy champions.

        """
        allies = ""
        enemies = ""
        for participant in participants:
            if participant['teamId'] == team_id:
                allies += "{}, ".format(cls.get_champ_name(participant['championId']))
            else:
                enemies += "{}, ".format(cls.get_champ_name(participant['championId']))

        allies = allies[:-2]
        enemies = enemies[:-2]

        return allies, enemies

    @classmethod
    def get_team_bans(cls, bans: list) -> str:
        """ Builds a list of a teams banned champions using that teams ban list

            Args:
                bans: a list containing ban dicts

            Returns:
                A string containing all of the banned champions for a team
        """
        list_of_bans = ""

        for ban in bans:
            list_of_bans += "{}, ".format(cls.get_champ_name(ban['championId']))

        list_of_bans = list_of_bans[:-2]
        return list_of_bans

    @classmethod
    def get_items(cls, participant_stats: dict) -> str:
        """ Builds a string containing all of the items purchased by a participant

            Args:
                participant_stats: a dictionary containing all of a participants stats

            Returns:
                A string of item names
        """
        champ_items = ""
        items = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
        for item in items:
            select_items_row = db.select([cls.items_table]).where(\
                    cls.items_table.c.key==participant_stats[item])

            items_row = LolParser.connection.execute(select_items_row).fetchone()
            if items_row:
                champ_items += "{}, ".format(items_row.name)
            else:
                champ_items += "NOT FOUND, " # I may eventually only return slots with items

        champ_items = champ_items[:-2]

        return champ_items

    @staticmethod
    def get_perks(participant_stats: dict) -> str:
        """ This function creates a string of perk ids. TODO: Get perk name from db when we can.

            Args:
                participant_stats: A dict from riot games containing stats info

            Returns:
                A string of perk ids
        """
        champ_perks = ""
        perks = ['perk0', 'perk1', 'perk2', 'perk3', 'perk4', 'perk5']
        for perk in perks:
            if perk:
                champ_perks += f"{participant_stats[perk]}, "

        champ_perks = champ_perks[:-2]
        return champ_perks

    @classmethod
    def get_team_data(cls, match_data: dict, account_id: str) -> Tuple[Dict, Dict, int]:
        """ Returns Team data for both teams, as well as the team_id for both teams

            Args:
                match_data: A dict containing lots of data about our match
                account_id: the account id of the player we're getting the team data of

            Returns:
                team_data: our teams data from this match
                enemy_team-data: enemy teams data from this match
                team_id: our teams team_id
        """

        participant_index = cls.get_participant_index(match_data['participantIdentities'],\
                account_id)

        participant = match_data['participants'][participant_index]

        team_id = participant['teamId']

        if team_id == 100:
            team_data = match_data['teams'][0]
            enemy_team_data = match_data['teams'][1]
            #enemy_team_id = 200
        elif team_id == 200:
            team_data = match_data['teams'][1]
            enemy_team_data = match_data['teams'][0]
            #enemy_team_id = 100

        return team_data, enemy_team_data, team_id


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
