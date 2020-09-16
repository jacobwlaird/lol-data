""" lolgather.py class

This class contains all the methods needed by the main script and by the lolaccount class
to be able to gather league of legends data. It handles all API calls to the riot games api.

"""
import json
import time
from typing import Dict
import configparser
import requests
from .lolparser import LolParser

class LolGather():
    """ Contains all the methods and functions needed by our other classes to return data from riot

        Attributes:
            _base_summoner_url (str): riot games api base endpoint for summoner
            _base_match_url    (str): riot games api base endpoint for match
            _account_name_url  (str): riot games api account name endpoint
            _matches_url       (str): riot games api matches endpoint
            _match_url         (str): riot games api individual match endpoint
            max_game_index     (int): The max index of games we'll search to using riot api

            _config         (obj): ConfigParser object for reading config file

            accounts    (list: str): Holds a list of all accounts we collect data for
            _api_key     (str): Our riot games API key pulled from config file

            match_id_list (list: str): Holds a list of games added this script run for logging
    """
    _base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
    _base_match_url = "https://na1.api.riotgames.com/lol/match/v4/"
    _account_name_url = "summoners/by-name/"
    _matches_url = "matchlists/by-account/"
    _match_url = "matches/"

    _config = configparser.ConfigParser()
    _config.read('./resources/python/general.cfg')
    max_game_index = 3000

    accounts = ['spaynkee', 'dumat', 'archemlis', 'stylus_crude', 'dantheninja6156', 'csqward']

    _api_key = _config.get('RIOT', 'api_key')
    new_match_data: Dict[int, Dict] = {}
    match_id_list = ""

    @classmethod
    def get_new_match_ids(cls, account_id: str) -> list:
        """ Gets an individual account's recently played match ids

            Args:
                account_id: The account id associated with our account

            Returns:
                A list containing MatchReferenceDto objects from riot games

        """
        game_index = 0
        player_matches = []

        while game_index < cls.max_game_index:
            try:
                player_matches_response = requests.get(''.join([cls._base_match_url,\
                        cls._matches_url, account_id, "?beginIndex=", str(game_index),\
                        "&endIndex=", str(game_index+100),\
                        "&api_key=", cls._api_key]))

                player_matches_response.raise_for_status()
                player_matches_response_dict = json.loads(player_matches_response.text)

                if not player_matches_response_dict['matches']:
                    break

                player_matches.append(player_matches_response_dict)
                game_index += 100
            except requests.exceptions.RequestException as e:
                LolParser.logger.critical("Get_account_info broke")
                if e.response.status_code == 403:
                    LolParser.logger.critical("Api key is probably expired")
                elif e.response.status_code == 429:
                    LolParser.logger.warning("Well that's an unfortunate timeout.")
                    time.sleep(10)
                else:
                    LolParser.logger.critical(e)

            time.sleep(.1)

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
            LolParser.logger.info(''.join(["getting match data for ", str(match_id)]))

            cls.add_id_to_match_list(match_id)

            time.sleep(.08) # this should keep us around the 20 per 1 second limit.

            matches_response = requests.get(''.join([cls._base_match_url, cls._match_url,\
                    str(match_id), "?api_key=", cls._api_key]))

            matches_response.raise_for_status()
            match_json = json.loads(matches_response.text)

            cls.add_match_data_to_new_match_data(match_id, match_json)

            return matches_response.text

        except requests.exceptions.RequestException as e:
            LolParser.logger.critical(e)
            LolParser.logger.warning("Get_match_data broke, trying again")
            time.sleep(10)
            cls.get_match_data(match_id)

        return ""

    @classmethod
    def add_id_to_match_list(cls, match_id: int):
        """ Adds the passed match_id to lolparser.match_id_list for update_run_info

            Args:
                match_id: the match_id to be added to the string
        """
        cls.match_id_list = cls.match_id_list + " " + str(match_id)


    @classmethod
    def add_match_data_to_new_match_data(cls, match_id: int, match_json: Dict):
        """ Adds the passed json data to lolparser.new_match_data dict with id = match_id

            Args:
                match_id: the match_id to be added to the dict
                match_json: the json data to be added to the class attribute
        """
        cls.new_match_data[match_id] = match_json

    @classmethod
    def get_user_id(cls, account_name: str) -> str:
        """ Hits the riot API and gets our account_id based on account_name

            Args:
                account_name: the account name we're getting the account_id for

            Returns:
                The account_id associated with this account from riot
        """
        try:
            account_response = requests.get(''.join([cls._base_summoner_url,\
                    cls._account_name_url, account_name, "?api_key=", cls._api_key]))
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            return account_data['accountId']
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 403:
                LolParser.logger.critical("Api key is probably expired")

            LolParser.logger.critical("get_user_id broke")

        return ""
