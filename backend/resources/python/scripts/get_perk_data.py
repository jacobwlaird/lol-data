""" get_perk_data

    This script hits a public api that has information about a particular patch of league of legends
    In particular, this script gets perk data.

    Note: This, like all other scripts have to be ran from resources/python for now.

    TODO: Store the current game version in a table somewhere so we can pull that instead
    of manually updating the game version

    Also, I'm not sure if this script works at all, and I don't feel like finding out now.
    Next time you read me, get this fixed, thanks.

"""
#pylint: disable=duplicate-code
import json
import requests
import sqlalchemy as db # type: ignore
from classes.lolparser import LolParser

def main():
    """ main function of get_perk_data

    """

    # I don't think this URL is real
    url = "http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json"
    res = requests.get(url)
    perk_res = json.loads(res.text)
    perk_data = perk_res['data']

    perk_table = db.Table('perks', LolParser.metadata, autoload=True,\
            autoload_with=LolParser.engine)

    for perk in perk_data:
        perk_table_insert = db.insert(perk_table).values(
                key=perk,
                name=perk_res['data'][perk]['name'])

        LolParser.connection.execute(perk_table_insert)

main()
