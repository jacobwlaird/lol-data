""" loldata.py

This script is the main script for the collection of data as part of
the loldat project. It creates an instance of the LolParser class
and creates instances of the LolAccount class for each of the accounts
we're collecting data from. It also logs info to our log file path
defined in our general.cfg file, and updates our script_runs table when
the script begins running, and when it finishes or fails.

Example:
    $ python3 loldata.py Manual

"""
from sys import argv
import logging
from sqlalchemy import exc
from classes.lolparser import LolParser
from classes.lolaccount import LolAccount

def main():
    """

    Creates a LolParser class, for all LolAccounts to use, and creates a LolAccount class
    each account we're tracking. Passes data to and from the LolParser as needed to get
    data stored into our database for each account.

    Arguments:
            Source -- the source of the run, be it manual, daily, or otherwise.
            To be stored in the script runs table.

    """
    # Create a new parser class
    parser = LolParser()

    if len(argv) != 2:
        return

    parser.store_run_info(argv[1])

    # Not really supposed to start logging this late, but whatever I guess....
    logging.basicConfig(filename=parser.log_file_name, level=logging.DEBUG)
    logging.info('\nScript is starting\n')

    try:
        # fix this when I figure it out this is causing tons of api calls that get me
        # timed out a lot.
        parser.max_game_index = 7000

        # Create a list of account objects with the account name set.
        account_list = [LolAccount(acc_name) for acc_name in LolParser.accounts]

        for acc in account_list:
            logging.info("Updating %s's matches", acc.account_name)

            # gets every match for this particular user
            acc.set_user_id()
            acc.get_user_matches()

            if not acc.user_matches:
                logging.info("No matches were found for %s", acc.account_name)

            # if the match isn't in the big list of data to be stored, add it. Otherwise, don't.
            for match in acc.user_matches:
                if match not in LolParser.new_match_data:
                    match_json = parser.get_match_data(str(match))
                    # add the match id to the list of matches here?
                    if match_json:
                        try:
                            parser.store_json_data(str(match), match_json)
                        except exc.IntegrityError as e:
                            logging.warning("Could not store json data, maybe it's already stored?")
                            logging.warning(e)
                            continue

            logging.info("Added %s new matches to %s's matches", len(acc.user_matches),\
                    acc.account_name)

            acc.update_player_table_stats()
            acc.update_team_data_table()

    # this line triggers the linter, but I think it has to stay to.
    except Exception as e:
        # if the run fails, update the table.
        parser.update_run_info("Failed", parser.match_id_list, str(e))

    parser.update_run_info("Success", parser.match_id_list, "No Errors")
    logging.info("Script run finished \n")
    return

if __name__ == "__main__":
    main()
