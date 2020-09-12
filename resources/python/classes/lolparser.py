""" lolparser.py class

This class contains all the methods needed by the main script and by the lolaccount class
to be able to gather and store league of legends data into a database.

"""
import logging
import json
import time
from datetime import datetime as date
import configparser
import requests
import sqlalchemy as db
from sqlalchemy import orm

class LolParser():
    """ Contains all the methods and functions needed by loldata.py and lolaccount.py
        Attributes:
            base_summoner_url (str): riot games api base endpoint for summoner
            base_match_url    (str): riot games api base endpoint for match
            account_name_url  (str): riot games api account name endpoint
            matches_url       (str): riot games api matches endpoint
            match_url         (str): riot games api individual match endpoint

            config         (obj): ConfigParser object for reading config file
            max_game_index (int): value denoting the max index of games we pull data for
            db_host        (str): database host address from config file
            db_user        (str): database user from config file
            db_pw          (str): database user password from config file
            db_name        (str): database name from config file

            engine        (obj): Sqlalchemy engine object created with config file contents
            connection    (obj): Sqlalchemy connection object created from the sqla engine
            metadata      (obj): Database metadata object
            session_maker (obj): Sqlalchemy orm session maker object

            champs_table     (obj): Sqlalchemy Table object for the champions table
            match_data_table (obj): Sqlalchemy Table object for the match_data table
            team_data_table  (obj): Sqlalchemy Table object for the team_data table
            items_table      (obj): Sqlalchemy Table object for the items table
            json_data_table  (obj): Sqlalchemy Table object for the json_data table
            runs_table       (obj): Sqlalchemy Table object for the script_runs table

            accounts    (list: str): Holds a list of all accounts we collect data for
            match_types (list: int): Holds a list of all game modes we collect data for
            api_key     (str): Our riot games API key pulled from config file

            match_id_list (list: str): Holds a list of games added this script run for logging
            log_file_name (str): Log file name pulled from config file

    """
    base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
    base_match_url = "https://na1.api.riotgames.com/lol/match/v4/"
    account_name_url = "summoners/by-name/"
    matches_url = "matchlists/by-account/"
    match_url = "matches/"

    config = configparser.ConfigParser()
    config.read('./resources/python/general.cfg')
    max_game_index = 7000

    db_host = config.get('DATABASE', 'db_id')
    db_user = config.get('DATABASE', 'db_user')
    db_pw = config.get('DATABASE', 'db_password')
    db_name = config.get('DATABASE', 'db_name')

    # db stuff.
    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(db_user,\
            db_pw, db_host, db_name), pool_size=100, max_overflow=100)
    connection = engine.connect()
    metadata = db.MetaData()
    session_maker = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False,\
            expire_on_commit=True)

    champs_table = db.Table('champions', metadata, autoload=True, autoload_with=engine)
    match_data_table = db.Table('match_data', metadata, autoload=True, autoload_with=engine)
    team_data_table = db.Table('team_data', metadata, autoload=True, autoload_with=engine)
    items_table = db.Table('items', metadata, autoload=True, autoload_with=engine)
    json_data_table = db.Table('json_data', metadata, autoload=True, autoload_with=engine)
    runs_table = db.Table('script_runs', metadata, autoload=True, autoload_with=engine)

    accounts = ['spaynkee', 'dumat', 'archemlis', 'stylus_crude', 'dantheninja6156', 'csqward']
    match_types = [400, 410, 420, 440, 700] # make sure this includes new types of matchmade games.

    api_key = config.get('RIOT', 'api_key')
    new_match_data = {}
    match_id_list = "" # this is for storing the ids in the script runs table.

    log_file_name = config.get('LOGGING', 'file_name')

    def __init__(self):
        logging.basicConfig(filename=self.log_file_name, level=logging.DEBUG)

    @classmethod
    def get_account_info(cls, account_id: str, start_index: int, end_index: int) -> dict:
        """ Gets an individual account's recently played match ids

            Args:
                account_id: The account id associated with our account
                start_index: The beginIndex param for matches api call
                end_index: the endIndex param for matches api call

            Returns:
                A dictionary containing MatchReferenceDto objects from riot games

        """
        try:
            player_matches = {}

            player_matches_response = requests.get(''.join([cls.base_match_url, cls.matches_url,\
                    account_id, "?beginIndex=", str(start_index), "&endIndex=", str(end_index),\
                    "&api_key=", cls.api_key]))

            player_matches_response.raise_for_status()
            player_matches = json.loads(player_matches_response.text)
        except requests.exceptions.RequestException as e:
            logging.critical("Get_account_info broke")
            if e.response.status_code == 403:
                logging.critical("Api key is probably expired")
            elif e.response.status_code == 429:
                logging.warning("Well that's an unfortunate timeout. I gotchu though fam.")
                time.sleep(10)
                return cls.get_account_info(account_id, start_index, end_index)
            else:
                logging.critical(e)


        return player_matches

    @classmethod
    def get_match_data(cls, match_id: int) -> str:
        """ Gets an individual matches data

            Args:
                match_id: The match id we're getting data for

            Returns:
                The text form of the json object we get from riot games,
                so that it can be stored in the json_data table.

        """
        try:
            logging.info(''.join(["getting match data for ", str(match_id)]))

            cls.add_id_to_match_list(match_id)

            time.sleep(.06) # this should keep us around the 20 per 1 second limit.

            matches_response = requests.get(''.join([cls.base_match_url, cls.match_url,\
                    str(match_id), "?api_key=", cls.api_key]))

            matches_response.raise_for_status()
            match_json = json.loads(matches_response.text)

            cls.add_match_data_to_new_match_data(match_id, match_json)

            return matches_response.text

        except requests.exceptions.RequestException as e:
            logging.critical(e)
            logging.warning("Get_match_data broke, trying again")
            time.sleep(10)
            cls.get_match_data(match_id)

    @classmethod
    def store_json_data(cls, match: str, json_formatted_string: str):
        """ Stores the json data into the json_data table

            Args:
                match: The match id we're storing data for
                json_formatted_string: The actual json data to be stored
        """
        json_sql_insert = db.insert(cls.json_data_table).values(match_id=match,\
                json_data=json_formatted_string)

        cls.connection.execute(json_sql_insert)

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

    @classmethod
    def add_id_to_match_list(cls, match_id: int):
        """ Adds the passed match_id to lolparser.match_id_list for update_run_info

            Args:
                match_id: the match_id to be added to the string
        """
        cls.match_id_list = cls.match_id_list + " " + str(match_id)


    @classmethod
    def add_match_data_to_new_match_data(cls, match_id: int, match_json: dict):
        """ Adds the passed json data to lolparser.new_match_data dict with id = match_id

            Args:
                match_id: the match_id to be added to the dict
                match_json: the json data to be added to the class attribute
        """
        cls.new_match_data[match_id] = match_json
