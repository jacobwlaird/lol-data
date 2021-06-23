""" loldata.py

This script is the main script for the collection of data as part of
the loldat project. It creates instances of the LolAccount class for each of the accounts
we're collecting data from. It creates Instances of the Parser, gatherer, and logger
and updates our script_runs table when the script begins running, as well as  when it
finishes or fails.

Example:
    $ python3 loldata.py Manual
    $ python3 loldata.py Manual 3000

"""
import json
import sys
from classes.lolconfig import LolConfig
from classes.lolparser import LolParser
from classes.lolaccount import LolAccount
from classes.lolgather import LolGather
from classes.lollogger import LolLogger

class LolData():
    """ Makes use of several other classes to download and store league of legends data.
        This class functions as the main data collection script.

        Attributes:
            config   (obj):  An instance of the config class. Used to get the log file name.
            parser   (obj):  An instance of the parser class. Used in several places.
            gatherer (obj):  An instance of the gather class. Used to get data from riots api.
            logger   (obj):  An instance of the logger class. used to log info to a log file.
            account_list (list: obj): A list of account class objects.

    """

    def __init__(self, source: str, max_game_index: int):
        """ Instantiates instances of several other classes, stores the initial script_run row
            and populates the account_list property.

            Arguments:
                source: The source of the script run. (Manual, Daily, Web, test, etc)
                max_game_index: The max index of games we'll search to.
        """

        self.config = LolConfig()
        self.parser = LolParser()
        self.gatherer = LolGather(max_game_index)
        self.logger = LolLogger(self.config.log_file_name)

        self.parser.store_run_info(source)
        self.logger.log_info('\nScript is starting\n')

        self.account_list = [LolAccount(acc_name) for acc_name in self.gatherer.accounts]

    def run(self):
        """

        Creates a LolAccount class instance for each account we're tracking. Updates the script_runs
        table when we start and finish a run.

        Arguments:
                Game_Index -(Optional)- The game index we're searching up to. A higher number for
                this drastically increases run time, so it defaults to 200 inside LolGather, and
                can be overwritten here.

        """

        #pylint: disable=broad-except # this is by design, as I want every exception to be caught.
        try:
            for acc in self.account_list:
                self.discover_new_matches(acc)

                if not acc.new_user_matches:
                    self.logger.log_info(f"No matches were found for {acc.account_name}")
                    continue

                self.store_new_match_data(acc)

                self.logger.log_info(\
                f"Added {len(acc.new_user_matches)} rows to match_data for {acc.account_name}")

                self.logger.log_info(f"Adding {acc.account_name}'s new matches to team_data table.")

                # get the matches already in the team_data, so we don't try to add those again.
                previous_team_data_matches = self.parser.get_previous_team_data_match_ids()
                self.store_new_team_data(acc, previous_team_data_matches)

        # this line triggers the linter, but I think it has to stay, so...
        except Exception as exc:
            except_string = f"Except: {type(exc)} {str(exc)}"
            self.parser.update_run_info("Failed", self.gatherer.match_id_list, except_string)
            self.logger.log_warning("Script run failed.\n")
            self.logger.log_warning(except_string)
            return

        self.parser.update_run_info("Success", self.gatherer.match_id_list, "No Errors")
        self.logger.log_info("Script run finished \n")
        return

    def discover_new_matches(self, acc: object):
        """ Determines if there are new matches for our account to be stored.

            Args:
                acc: An instance of the account class representing the player we're getting data for

        """
        self.logger.log_info(f"Updating {acc.account_name}'s matches in match_data")

        acc.account_id = self.gatherer.get_account_id(acc.account_name)

        # Gets all the recent games the account has played
        recent_player_matches = self.gatherer.get_match_reference_dto(acc.account_id)

        # gets a list of matches we've already stored for this player.
        acc.previous_player_matches = self.parser.get_previous_player_match_data_ids(\
                acc.account_name)

        # determines only the new matches we still need to save.
        acc.new_user_matches = self.gatherer.get_unstored_match_ids(\
                acc.previous_player_matches, recent_player_matches, LolAccount.match_types)

    def store_new_match_data(self, acc):
        """ Makes the calls needed to the gatherer and parser to actually get and store data for a
            match, for each match_id in acc.new_user_matches

            Args:
                acc: An instance of the account class representing the player we're getting data for

        """
        for match in acc.new_user_matches:
            # If we don't have the data for this match yet.
            if match not in self.gatherer.new_match_data:
                # get the match data from the gatherer
                match_json_str = self.gatherer.get_match_data(match)
                match_data = json.loads(match_json_str)

                self.parser.store_json_data(match, match_json_str)
            else:
                # We did already have the match data, so we just pull that data from the gatherer.
                match_data = self.gatherer.new_match_data[match]

            # Store the player data for this match into the player data table.
            self.parser.insert_match_data_row(match_data, acc.account_name, acc.account_id)

    def store_new_team_data(self, acc, previous_team_data_matches: list):
        """ Makes the calls needed to the gatherer and parser to actually get and store team data
            for each match_id in acc.new_user_matches

            Args:
                acc: An instance of the account class representing the player we're getting data for
                previous_team_data_matches: All of the rows currently in the team data table.

        """
        for match in acc.new_user_matches:
            # if the match is not currently stored, we need to store it. If it is already stored,
            # That means this player played this particular match with another one of our
            # watched accounts, so we should update that team_data row instead.
            if match not in previous_team_data_matches:
                # Grab the data from the new_match_data object.
                match_data = self.gatherer.new_match_data[match]

                # and insert it into the team_data table.
                self.parser.insert_team_data_row(match_data,\
                        acc.account_name, acc.account_id)

            else:
                # update the row instead of adding a new one.
                self.parser.update_team_data_row(match, acc.account_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Expected an argument denoting run 'source'. (Manual, test, etc)")
        sys.exit()

    run_source = sys.argv[1]

    if len(sys.argv) == 3:
        try:
            max_index = int(sys.argv[2])
        except ValueError:
            print("Excpeted int for 3rd parameter")
            sys.exit()

    data = LolData(run_source, max_index)
    data.run()
