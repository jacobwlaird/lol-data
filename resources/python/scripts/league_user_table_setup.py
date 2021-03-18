""" user_table_setup

    This small script creates the users table.

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
from sqlalchemy import Column, Table, Integer, String, MetaData, exc # type: ignore
from classes.lolparser import LolParser

def main():
    """ main function of user_table_setup imports from LolParser and creates the table.

    """
    #pylint: disable=no-value-for-parameter # this is a false positive?

    try:
    # drop the users table
        league_users_table = Table('league_users', LolParser.metadata, autoload=True,\
                autoload_with=LolParser.engine)
        league_users_table.drop(LolParser.engine)
    except exc.NoSuchTableError:
        print("Hey, the league_users table probably didn't exist,\
                so we're just gonna create it instead of dropping it and then creating it.")

    league_users_table = Table('league_users',
            MetaData(),
            Column('id', Integer, primary_key=True, autoincrement=True),\
            Column('summoner_name', String(30)),
            Column('riot_id', String(400)))

    league_users_table.create(LolParser.engine)

main()
