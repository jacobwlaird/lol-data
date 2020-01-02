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

def main():
    # Create a new parser class
    parser = LolParser()

    # Set a couple things
    LolParser.max_game_index = 100
    LolParser.accounts = ['spaynkee', 'dumat']

    # Create a list of account objects with the account name set.
    account_list = [LolAccount(acc_name) for acc_name in LolParser.accounts]
    
    for acc in account_list:
        print("Updating {}'s matches".format(acc.account_name))

        # gets every match for this particular user.
        acc.get_user_matches()

        if not acc.user_matches:
            print("No matches were found for {}".format(acc.account_name))
            
        # if the match isn't in the big list of data to be stored, add it. Otherwise, don't.
        for match in acc.user_matches:
            if match not in LolParser.new_match_data:
                parser.get_match_data(match)

        print("Added {} new matches to {}'s matches".format(len(acc.user_matches), acc.account_name))

        acc.update_player_table_stats()

        # updating the user_match_history table after getting the list of matches

        # update player opponent needs a big change.
        
        # updating the matches table

        # ??

    return

if __name__ == "__main__":
    print("here we go...")
    main()
