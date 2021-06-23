""" lolgather.py class

This class contains all the methods needed by the main script and by the lolaccount class
to be able to gather league of legends data. It handles all API calls to the riot games api.

"""
import json
import time
from typing import Dict
import requests
from .lolparser import LolParser
from .lollogger import LolLogger
from .lolconfig import LolConfig

#pylint: disable=too-many-instance-attributes # This is okay.
class LolGather():
    """ Contains all the methods and functions needed by our other classes to return data from riot

        Attributes:
            base_summoner_url (str): riot games api base endpoint for summoner
            account_name_url  (str): riot games api account name endpoint
            _base_match_url    (str): riot games api base endpoint for match
            _matches_url       (str): riot games api matches endpoint
            _match_url         (str): riot games api individual match endpoint

            config             (obj): Config Class that does all our config stuff.

            accounts    (list: str): Holds a list of all accounts we collect data for
            match_id_list (list: str): Holds a list of games added this script run for logging
    """

    def __init__(self, max_game_index=200):
        self.base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
        self.account_name_url = "summoners/by-name/"
        self._base_match_url = "https://na1.api.riotgames.com/lol/match/v4/"
        self._matches_url = "matchlists/by-account/"
        self._match_url = "matches/"
        self.max_game_index = max_game_index

        self.lolparser = LolParser()
        self.config = LolConfig()
        self.accounts = self.lolparser.get_summoner_names()
        self.new_match_data: Dict[int, Dict] = {}
        self.match_id_list = ""
        self.logger = LolLogger(self.config.log_file_name)

    def get_match_reference_dto(self, account_id: str) -> list:
        """ Gets an individual account's recently played match ids.

            Args:
                account_id: The account id associated with our account

            Returns:
                A list containing MatchReferenceDto objects from riot games.

        """
        game_index = 0
        player_matches = []

        # keeps looping until we get to the max_game_index
        # a higher max game index makes us check further back in time.
        while game_index < self.max_game_index:
            try:
                player_matches_response = requests.get(''.join([self._base_match_url,\
                        self._matches_url, account_id, "?beginIndex=", str(game_index),\
                        "&endIndex=", str(game_index+100),\
                        "&api_key=", self.config.api_key]))

                player_matches_response.raise_for_status()
                player_matches_response_dict = json.loads(player_matches_response.text)

                if not player_matches_response_dict['matches']:
                    break

                player_matches.append(player_matches_response_dict)
                game_index += 100
            except requests.exceptions.RequestException as exc:
                self.logger.log_critical("Get_account_info broke")
                if exc.response.status_code == 403:
                    self.logger.log_critical("Api key is probably expired")
                elif exc.response.status_code == 429:
                    self.logger.log_warning("Well that's an unfortunate timeout.")
                    time.sleep(10)
                else:
                    self.logger.log_critical(exc)

            time.sleep(.1)

        return player_matches

    def get_match_data(self, match_id: int) -> str:
        """ Gets an individual matches data

            Args:
                match_id: The match id we're getting data for

            Returns:
                The text form of the json object we get from riot games,
                so that it can be stored in the json_data table.

        """
        try:
            self.logger.log_info(''.join(["getting match data for ", str(match_id)]))

            # add match_id to match list
            self.match_id_list = self.match_id_list + " " + str(match_id)

            time.sleep(.08) # this should keep us around the 20 per 1 second limit.

            matches_response = requests.get(''.join([self._base_match_url, self._match_url,\
                    str(match_id), "?api_key=", self.config.api_key]))

            matches_response.raise_for_status()
            match_json = json.loads(matches_response.text)

            self.new_match_data[match_id] = match_json

            return matches_response.text

        except requests.exceptions.RequestException as exc:
            self.logger.log_critical(exc)
            self.logger.log_warning("Get_match_data broke, trying again")
            time.sleep(10)
            self.get_match_data(match_id)

        return ""

    def get_account_id(self, account_name: str) -> str:
        """ Hits the riot API and gets our account_id based on account_name

            Args:
                account_name: the account name we're getting the account_id for

            Returns:
                The account_id associated with this account from riot
        """
        try:
            account_response = requests.get(''.join([self.base_summoner_url,\
                    self.account_name_url, account_name, "?api_key=", self.config.api_key]))
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            return account_data['accountId']
        except requests.exceptions.RequestException as exc:
            if exc.response.status_code == 403:
                self.logger.log_critical("Api key is probably expired")

            self.logger.log_critical("get_user_id broke")

        return ""

    @staticmethod
    def get_unstored_match_ids(prev_matches: list, new_matches: list,\
            match_types: list) -> list:
        """ Compares a set of previous match ids with the data we return from riot to determine
            which matches we will need to get data for.

            Args:
                prev_matches: the list of matches we already have data for.
                new_matches: A list containing data objects that include recent game ids.
                match_types: A list of the match types to include in the comparison.

            Returns:
                A list of match ids a player was in, but that we don't have stored yet.
        """

        unstored_match_ids = []

        for page in new_matches:
            for match in page['matches']:
                if match['queue'] in match_types:
                    if match['gameId'] not in prev_matches:
                        unstored_match_ids.append(match['gameId'])

        return unstored_match_ids
