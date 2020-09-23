""" get_item_data

    This script hits a public api that has information about a particular patch of league of legends
    In particular, this script gets item data.

    Note: This, like all other scripts have to be ran from resources/python for now.

    TODO: Store the current game version in a table somewhere so we can pull that instead
    of manually updating the game version

"""
import json
import requests
import sqlalchemy as db # type: ignore
from classes.lolparser import LolParser

#Update the version number in the future if we need to.
def main():
    """ main function of get_item_data

    """
    url = "http://ddragon.leagueoflegends.com/cdn/10.19.1/data/en_US/item.json"
    res = requests.get(url)
    item_res = json.loads(res.text)
    item_data = item_res['data']

    item_table = db.Table('items', LolParser.metadata, autoload=True,\
            autoload_with=LolParser.engine)

    for item in item_data:
        item_table_insert = db.insert(item_table).values(
                key=item,
                name=item_res['data'][item]['name'])

        LolParser.connection.execute(item_table_insert)

main()
