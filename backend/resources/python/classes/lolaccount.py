""" lolaccount.py class

This class gets and sets all data we need to store an accounts data, and contains the functions
needed to interface with the lolparser class to actually store the data.

"""
from .lolparser import LolParser
from .lolgather import LolGather
class LolAccount():
    """ Contains all the methods and functions needed to store the gathered data into the database

        Attributes:
            account_name      (str): the account name for our account
            new_user_matches  (list: int): list of new matches to be added to the db for this player
            account_id        (str): the account_id of this account from riot
            _previous_player_matches (list: int): the list of games we currently have for this acc
            _match_types      (list: int): Holds a list of all game modes we collect data for

    """

    _match_types = [400, 410, 420, 440, 700] # make sure this includes new types of matchmade games

    def __init__(self, name):
        self.account_name = name
        self.new_user_matches = []
        self.account_id = LolGather.get_user_id(self.account_name)
        self._previous_player_matches = []

        self.get_previous_player_matches()
        self.get_new_user_matches()

    def get_previous_player_matches(self):
        """ Instantiates the previous_player_matches list

        """
        player_match_history = LolParser.select_previous_matches(self.account_name)

        for match in player_match_history:
            self._previous_player_matches.append(match.match_id)

    @staticmethod
    def get_previous_team_data_match_ids() -> list:
        """ Creates and Returns a list of the match_ids already in team_match_data

            Return:
                A list of integers containing all match_ids currently in team_data
        """
        player_match_history = LolParser.select_previous_team_data_matches()
        previous_team_data_matches = []

        for row in player_match_history:
            previous_team_data_matches.append(row.match_id)

        return previous_team_data_matches

    def get_new_user_matches(self):
        """ Stores the new match_ids we're getting data for into new_user_matches

        """
        player_matches = LolGather.get_new_match_ids(self.account_id)

        for page in player_matches:
            for match in page['matches']:
                if match['gameId'] not in self._previous_player_matches:
                    if match['queue'] in self._match_types:
                        self.new_user_matches.append(match['gameId'])

    def store_player_match_data(self):
        """ Gets match_data from LolGather and sends it to LolParser to be stored in match_data

        """
        for match in self.new_user_matches:
            match_data = LolGather.new_match_data[match]
            LolParser.insert_player_table_data(match_data, self.account_name,\
                    self.account_id)


    def store_team_data_table_row(self):
        """ Gets match_data from LolGather and sends it to LolParser to be stored in team_data

        """
        previous_team_matches = LolAccount.get_previous_team_data_match_ids()

        for match in self.new_user_matches:
            if match not in previous_team_matches:
                match_data = LolGather.new_match_data[match]
                LolParser.insert_team_data_table_row(match_data, self.account_name, self.account_id)
            else:
                LolParser.update_team_data_table_row(match, self.account_name)
