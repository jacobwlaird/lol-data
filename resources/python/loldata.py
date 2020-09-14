""" loldata.py

This script is the main script for the collection of data as part of
the loldat project. It creates an instance of the LolParser class
and creates instances of the LolAccount class for each of the accounts
we're collecting data from. It also calls to LolParser to log info to our log 
file, and updates our script_runs table when the script begins running,
and when it finishes or fails.

Example:
    $ python3 loldata.py Manual

"""
from sys import argv
from sqlalchemy import exc
from classes.lolparser import LolParser
from classes.lolaccount import LolAccount

def main():
    """

    Creates a LolAccount class for each account we're tracking. 
    Passes data to and from the LolParser as needed to get
    data stored into our database for each account.

    Arguments:
            Source -- the source of the run, be it manual, daily, or otherwise.
            To be stored in the script runs table.

    """
    if len(argv) != 2:
        return

    LolParser.store_run_info(argv[1])
    LolParser.logger.info('\nScript is starting\n')

    try:
        LolParser.max_game_index = 3000 # increase this if we want to run further back

        account_list = [LolAccount(acc_name) for acc_name in LolParser.accounts]

        for acc in account_list:
            LolParser.logger.info("Updating %s's matches", acc.account_name)

            acc.set_new_user_matches()

            if not acc.new_user_matches:
                LolParser.logger.info("No matches were found for %s", acc.account_name)

            for match in acc.new_user_matches:
                if match not in LolParser.new_match_data:
                    match_json = LolParser.get_match_data(match)

                    if match_json:
                        try:
                            LolParser.store_json_data(str(match), match_json)
                        except exc.IntegrityError as e:
                            LolParser.logger.warning("Could not store json data, maybe it's already stored?")
                            LolParser.logger.warning(e)
                            continue

            LolParser.logger.info("Added %s new matches to %s's matches", len(acc.new_user_matches),\
                    acc.account_name)

            acc.update_player_table_stats()
            acc.update_team_data_table()

    # this line triggers the linter, but I think it has to stay to.
    except Exception as e:
        # if the run fails, update the table.
        LolParser.update_run_info("Failed", LolParser.match_id_list, str(e))

    LolParser.update_run_info("Success", LolParser.match_id_list, "No Errors")
    LolParser.logger.info("Script run finished \n")
    return

if __name__ == "__main__":
    main()
