""" enemy_dragon_rift_herald_fill

    This script goes through all the json data in our json_data table, and fills in columns
    that we might have added recently. In particular, this script fills the enemy_dragon_kills
    and enemy_rift_herald_kills columns in team_data

    Note: This, like all other scripts have to be ran from resources/python for now.

    Also note that this is not the way this script should be written, but I'm not taking the
    time to rework a script that won't be used in the future. Still, there's some usefulness
    in seeing the order I did things when I wrote this script originally, so I'll document it
    and make the next script like this that I write a better example.

"""
# pylint: skip-file
import json
import configparser
from sqlalchemy import orm
import pandas as pd # We won't be installing pandas in this env.
import sqlalchemy as db
from classes.lolparser import LolParser

def main():
    """ main function of enemy_dragon_rift_herald_fill

    """

    # this script is gonna parse through the json table, get our info, and backfill our table.
    config = configparser.ConfigParser()
    config.read('./resources/python/general.cfg')

    db_host = config.get('DATABASE', 'db_id')
    db_user = config.get('DATABASE', 'db_user')
    db_pw = config.get('DATABASE', 'db_password')
    db_name = config.get('DATABASE', 'db_name')

    engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user,\
            db_pw, db_host, db_name), pool_size=100, max_overflow = 100)

    engine.connect()
    metadata = db.MetaData()
    orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)

    db.Table('team_data', metadata, autoload=True, autoload_with=engine)

    old_data = {}

    select_old_data = "SELECT * FROM team_data;"
    old_data = pd.read_sql(select_old_data, LolParser.connection)

    new_data = {}

    select_new_data = "SELECT * FROM json_data;"
    new_data = pd.read_sql(select_new_data, LolParser.connection)

    for row in new_data['match_id']:
        print("Updating match {}".format(row))

        if old_data[old_data['match_id'] == row] is not None:
            json_dict = json.loads(new_data[new_data['match_id'] == row]['json_data'].values[0])

            teams = json_dict['teams']
            game_result = old_data[old_data['match_id'] == row]['win'].values[0]

            enemy_team = {}

            if teams[0]['win'] == game_result:
                enemy_team = teams[1]
            else:
                enemy_team = teams[0]

            enemy_dragon_kills = enemy_team['dragonKills']
            enemy_rift_herald_kills = enemy_team['riftHeraldKills']

            team_data_table_update = db.update(LolParser.team_data_table).values(
               enemy_dragon_kills=enemy_dragon_kills,
               enemy_rift_herald_kills=enemy_rift_herald_kills
            ).where(LolParser.team_data_table.c.match_id==row)

            LolParser.connection.execute(team_data_table_update)
        else:
            print("Hey, uh, {} isn't in our team_data table. Fix me sometime?".format(row))
            continue

main()
