""" lolaccount.py class

This class gets and sets all data we need to store an accounts data, and contains the functions
needed to interface with the lolparser class to actually store the data.

"""
#pylint: disable=too-few-public-methods # This is okay.
class LolAccount():
    """ Contains all the methods and functions needed to store the gathered data into the database

        Attributes:
            match_types      (list: int): Holds a list of all game modes we collect data for

            account_name      (str): the account name for our account
            new_user_matches  (list: int): list of new matches to be added to the db for this player
            account_id        (str): the account_id of this account from riot
            previous_player_matches (list: int): the list of games we currently have for this acc
            new_match_data    (dict): Holds all of the actual match data for each match?

    """

    match_types = [400, 410, 420, 440, 700] # make sure this includes new types of matchmade games

    def __init__(self, name):
        self.account_name = name
        self.new_user_matches = []
        self.account_id = None
        self.previous_player_matches = []
        self.new_match_data = {}
