""" loldata.py

This script is the main script for the collection of data as part of
the loldat project. It creates instances of the LolAccount class for each of the accounts
we're collecting data from. It also calls to LolParser to log info to our log
file, and updates our script_runs table when the script begins running,
and when it finishes or fails.

Example:
    $ python3 loldata.py Manual

"""
from sys import argv
from classes.lolparser import LolParser
from classes.lolaccount import LolAccount
from classes.lolgather import LolGather

def main():
    """

    Creates a LolAccount class for each account we're tracking. Updates the script_runs
    table when we start and finish a run.

    Arguments:
            Source -- the source of the run, be it manual, daily, or otherwise.
            To be stored in the script runs table.

    """

    #pylint: disable=broad-except # this is by design, as I want every exception to be caught here.
    if len(argv) != 2:
        return

    LolParser.store_run_info(argv[1])
    LolParser.logger.info('\nScript is starting\n')

    try:
        LolGather.max_game_index = 3000 # increase this if we want to run further back

        account_list = [LolAccount(acc_name) for acc_name in LolGather.accounts]

        for acc in account_list:
            LolParser.logger.info("Updating %s's matches", acc.account_name)

            if not acc.new_user_matches:
                LolParser.logger.info("No matches were found for %s", acc.account_name)
                continue

            for match in acc.new_user_matches:
                if match not in LolGather.new_match_data:
                    match_json = LolGather.get_match_data(match)
                    if match_json:
                        LolParser.store_json_data(match, match_json)

            acc.store_player_match_data()

            LolParser.logger.info("Added %s new matches to %s's matches",\
                    len(acc.new_user_matches), acc.account_name)

            LolParser.logger.info("Adding %s's new matches to team_data table.", acc.account_name)
            acc.store_team_data_table_row()

    # this line triggers the linter, but I think it has to stay, so...
    except Exception as e:
        LolParser.update_run_info("Failed", LolGather.match_id_list, f"Except: {type(e)} {str(e)}")

    LolParser.update_run_info("Success", LolGather.match_id_list, "No Errors")
    LolParser.logger.info("Script run finished \n")
    return

if __name__ == "__main__":
    main()
