import configparser
import pymysql
import pymysql.cursors as cursors
import requests
import json
import time
import pandas as pd
import sqlalchemy as db
from classes.lolparser import LolParser
from classes.lolaccount import LolAccount
from sys import argv
import logging

def main(argv):
    # Create a new parser class
    parser = LolParser()
    parser.store_run_info(argv[1])

    # Not really supposed to start logging this late, but whatever I guess....
    logging.basicConfig(filename=parser.log_file_name,level=logging.DEBUG)
    logging.info('\nScript is starting\n')

    try:
        # Set a couple things
        if len(argv) == 3:
            LolParser.max_game_index = int(argv[2])
        else:
            parser.max_game_index = 7000

        # Create a list of account objects with the account name set.
        account_list = [LolAccount(acc_name) for acc_name in LolParser.accounts]
        
        for acc in account_list:
            logging.info("Updating {}'s matches".format(acc.account_name))

            # gets every match for this particular user
            acc.set_user_id()
            acc.get_user_matches()

            if not acc.user_matches:
                logging.info("No matches were found for {}".format(acc.account_name))
                
            # if the match isn't in the big list of data to be stored, add it. Otherwise, don't.
            for match in acc.user_matches:
                if match not in LolParser.new_match_data:
                    match_json = parser.get_match_data(match)
                    # add the match id to the list of matches here?
                    if match_json:
                        try:
                            parser.store_json_data(match, match_json)
                        except Exception as e:
                            logging.warning("Could not store json data, maybe it's already stored?")
                            logging.warning(e)
                            continue

            logging.info("Added {} new matches to {}'s matches".format(len(acc.user_matches), acc.account_name))

            acc.update_player_table_stats()
            acc.update_team_data_table()

    except Exception as e:
        # if the run fails, update the table.
        parser.update_run_info("Failed", parser.match_id_list, str(e))

    parser.update_run_info("Success", parser.match_id_list, "No Errors")
    logging.info("Script run finished \n")
    return

if __name__ == "__main__":
    main(argv)
