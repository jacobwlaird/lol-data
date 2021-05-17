""" update_db_from_api.py

This script will populate the match_data,team_data, and league_users tables in the db
specified in the config file.

The new data comes from the public api endpoints I have set up for these tables.
This is useful if we're creating

a new test database, or if we want to copy the data to anywhere that doesn't have
access to a sql dump.

"""
import json
import requests
from classes.lolparser import LolParser
import sqlalchemy as db

def main():
    """
        We make 3 requests to our public endpoints, and populate the db with that data.

    """

    print("Sup, it ran?")
    return

    #pylint: disable=broad-except # this is by design, as I want every exception to be caught here.

    my_team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data")
    matches = json.loads(my_team_data.text)

    LolParser.connection.execute(db.insert(LolParser.team_data_table), matches)

    users = ['Spaynkee', 'Dumat', 'Archemlis', 'Stylus_Crude', 'dantheninja6156', 'Csqward']
    for user in users:
        user_data = get_player_data(user)
        LolParser.connection.execute(db.insert(LolParser.match_data_table), user_data)

    my_league_user_data = requests.get("http://paulzplace.asuscomm.com/api/get_league_users")

    league_users = json.loads(my_league_user_data.text)

    LolParser.connection.execute(db.insert(LolParser.league_users_table), league_users)

def get_player_data(player):
    """
        Gets an individual players data from the public api.

        Args:
            player: the name of the players data we're returning

        Returns:
            an array containing every row for our user in the match_data table.

    """
    return json.loads(requests.get(\
            f"http://paulzplace.asuscomm.com/api/get_user_data?name={player}").text)

if __name__ == "__main__":
    main()
