""" update_db_from_api.py

This script will populate the all of the tables in the db
specified in the config file.

The new data comes from the public api endpoints I have set up for these tables.
This is useful if we're creating a new test database, or if we want to copy the
data to anywhere that doesn't have access to a sql dump.

"""
import sys
import json
import requests
from classes.loldb import LolDB
from classes.lolconfig import LolConfig
from classes.models import TeamData, MatchData, ScriptRuns, Champions, Items, JsonData, LeagueUsers

#pylint: disable=too-many-locals # This is okay.
def main():
    """
        We make at least 7 requests to our public endpoints, and populate the db with that data.

    """

    # we need to drop all the existing tables so we can re populate.

    config = LolConfig()
    our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)

    our_db.metadata.drop_all(our_db.engine)
    our_db.session.commit()

    our_db.metadata.create_all(our_db.engine)
    our_db.session.commit()

    print("Getting script runs")
    # script runs table.
    my_script_run_data = requests.get("http://paulzplace.asuscomm.com/api/get_script_runs")
    script_runs = json.loads(my_script_run_data.text)
    our_db.session.add_all([ScriptRuns(**run) for run in script_runs])

    print("getting team data")
    # team data table
    my_team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data")
    matches = json.loads(my_team_data.text)
    our_db.session.add_all([TeamData(**match) for match in matches])

    print("getting user data")
    # match data table
    users = ['Spaynkee', 'Dumat', 'Archemlis', 'Stylus Crude', 'dantheninja6156', 'Csqward']
    for user in users:
        user_data = get_player_data(user)
        our_db.session.add_all([MatchData(**match) for match in user_data])

    print("getting league users")
    #league_users table
    my_league_user_data = requests.get("http://paulzplace.asuscomm.com/api/get_league_users")
    league_users = json.loads(my_league_user_data.text)
    our_db.session.add_all([LeagueUsers(**user) for user in league_users])


    print("getting champions")
    #champions table
    my_champion_data = requests.get("http://paulzplace.asuscomm.com/api/get_champions")
    champions = json.loads(my_champion_data.text)
    our_db.session.add_all([Champions(**champ) for champ in champions])

    print("getting items")
    # items table
    my_item_data = requests.get("http://paulzplace.asuscomm.com/api/get_items")
    items = json.loads(my_item_data.text)
    our_db.session.add_all([Items(**item) for item in items])

    print("getting json data. Big Oof")
    # json data
    my_json_data_data = requests.get("http://paulzplace.asuscomm.com/api/get_json_data")
    json_data = json.loads(my_json_data_data.text)
    our_db.session.add_all([JsonData(**json) for json in json_data])
    our_db.session.commit()

def get_player_data(player: str) -> list:
    """
        Gets an individual players data from the public api.

        Args:
            player (str): the name of the players data we're returning

        Returns:
            an array containing every row for our user in the match_data table.

    """
    return json.loads(requests.get(\
            f"http://paulzplace.asuscomm.com/api/get_user_data?name={player}").text)

if __name__ == "__main__":
    # If you're gonna remove this exit, you better be in test. or else.
    sys.exit()
    main()
