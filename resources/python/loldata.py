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

def main():
    # Create a new parser class
    parser = LolParser()

    # Set a couple things
    if len(argv) == 2:
        LolParser.max_game_index = int(argv[1])
    else:
        parser.max_game_index = 7000

    # Create a list of account objects with the account name set.
    account_list = [LolAccount(acc_name) for acc_name in LolParser.accounts]
    
    for acc in account_list:
        print("Updating {}'s matches".format(acc.account_name))

        # gets every match for this particular user
        acc.set_user_id()
        acc.get_user_matches()

        if not acc.user_matches:
            print("No matches were found for {}".format(acc.account_name))
            
        # if the match isn't in the big list of data to be stored, add it. Otherwise, don't.
        for match in acc.user_matches:
            if match not in LolParser.new_match_data:
                match_json = parser.get_match_data(match)
                if match_json:
                    parser.store_json_data(match, match_json)

        print("Added {} new matches to {}'s matches".format(len(acc.user_matches), acc.account_name))

        acc.update_player_table_stats()
        acc.update_team_data_table()

    return

if __name__ == "__main__":
    print("here we go...")
    main()
