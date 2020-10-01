""" user_table_setup

    This small script creates the users table, and then populates it by hitting riots api

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
import json
from sqlalchemy import Column, Table, Integer, String, MetaData # type: ignore
from classes.lolparser import LolParser
from classes.lolgather import LolGather
import requests

def main():
    """ main function of user_table_setup imports from LolParser and LolGather and creates the table

    """
    #pylint: disable=no-value-for-parameter # this is a false positive?

    # drop the users table
    league_users_table = Table('league_users', LolParser.metadata, autoload=True,\
            autoload_with=LolParser.engine)
    league_users_table.drop(LolParser.engine)

    league_users_table = Table('league_users',
            MetaData(),
            Column('id', Integer, primary_key=True, autoincrement=True),\
            Column('summoner_name', String(30)),
            Column('riot_id', String(400)))

    league_users_table.create(LolParser.engine)

    for account in LolGather.accounts:
        account_response = requests.get(''.join([LolGather.base_summoner_url,\
                LolGather.account_name_url, account, "?api_key=", LolGather.api_key]))
        account_response.raise_for_status()
        account_data = json.loads(account_response.text)

        league_user_insert = league_users_table.insert().values(
                summoner_name=account_data['name'],\
                riot_id=account_data['accountId'])

        LolParser.connection.execute(league_user_insert)

main()
