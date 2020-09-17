""" data-base-setupt-v2

    This script creates most of the tables in our database incase we need to reset it, or if we
    need to create the db on a different sever or whatever.

    In particular, this script creates match_data, team_data, and script_runs.
    champions, items, ?perks? and other tables will likely be in their own scripts

"""
from sqlalchemy import Column, Table, Integer,\
        String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData

from classes.lolparser import LolParser

# drop the team_match_data table.
def main():
    """ main function of data-base-setup-v2 tries to drop tables before creating them again.

    """
    try:
        team_data_table = Table('team_data', LolParser.metadata,\
                autoload=True, autoload_with=LolParser.engine)
        team_data_table.drop(LolParser.engine)
    except:
        print("Hey, the team_data table probably didn't exist,\
                so we're just gonna create it instead of dropping it and then creating it.")

    # create the team_match_data table
    team_data_table = Table('team_data',\
            MetaData(),\
            Column('match_id', BigInteger, primary_key=True),\
            Column('game_version', String(40)),\
            Column('win', String(10)),\
            Column('participants', String(80)),\
            Column('first_blood', Boolean),\
            Column('first_baron', Boolean),\
            Column('first_tower', Boolean),\
            Column('first_dragon', Boolean),\
            Column('first_inhib', Boolean),\
            Column('first_rift_herald', Boolean),\
            Column('ally_dragon_kills', Integer),\
            Column('ally_rift_herald_kills', Integer),\
            Column('enemy_dragon_kills', Integer),\
            Column('enemy_rift_herald_kills', Integer),\
            Column('inhib_kills', Integer),\
            Column('bans', String(80)),\
            Column('enemy_bans', String(80)),\
            Column('allies', String(80)),\
            Column('enemies', String(80)),\
            Column('start_time', TIMESTAMP),\
            Column('duration', Time))

    team_data_table.create(LolParser.engine)

    try:
        matches_table = Table('match_data', LolParser.metadata,\
                autoload=True, autoload_with=LolParser.engine)
        matches_table.drop(LolParser.engine)
    except:
        print("Hey, the match_data table probably didn't\
               exist, so we're just gonna create it instead of dropping it and then creating it.")

    matches_table = Table('match_data',\
            MetaData(),\
            Column('id', Integer, primary_key=True, autoincrement=True),\
            Column('match_id', BigInteger),\
            Column('player', String(40)),\
            Column('role', String(10)),\
            Column('champion', Integer),\
            Column('champion_name', String(25)),\
            Column('enemy_champion', Integer),\
            Column('enemy_champion_name', String(25)),\
            Column('first_blood', Boolean),\
            Column('first_blood_assist', Boolean),\
            Column('kills', Integer),\
            Column('deaths', Integer),\
            Column('assists', Integer),\
            Column('damage_to_champs', Integer),\
            Column('damage_to_turrets', Integer),\
            Column('gold_per_minute', Float),\
            Column('creeps_per_minute', Float),\
            Column('xp_per_minute', Float),\
            Column('wards_placed', Integer),\
            Column('vision_wards_bought', Integer),\
            Column('wards_killed', Integer),\
            Column('items', String(200)),\
            Column('perks', String(100))\
            )

    matches_table.create(LolParser.engine)

    try:
        runs_table = Table('script_runs', LolParser.metadata, autoload=True,\
                autoload_with=LolParser.engine)
        runs_table.drop(LolParser.engine)
    except:
        print("Hey, the script_runs table probably didn't exist,\
                so we're just gonna create it instead of dropping it and then creating it.")

    runs_table = Table('script_runs',\
            MetaData(),\
            Column('id', Integer, primary_key=True, autoincrement=True),\
            Column('source', String(50)),\
            Column('status', String(20)),\
            Column('matches_added', String(60000)),\
            Column('start_time', TIMESTAMP),\
            Column('end_time', TIMESTAMP),\
            Column('message', String(1000))\
            )

    runs_table.create(LolParser.engine)


main()
