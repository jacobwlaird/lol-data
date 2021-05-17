""" get_champion_data

    This script hits a public api that has information about a particular patch of league of legends
    In particular, this script gets champion data.

    Note: This, like all other scripts have to be ran from resources/python for now.

    TODO: Store the current game version in a table somewhere so we can pull that instead
    of manually updating the game version

"""
#pylint: skip-file # I don't want to do this, but I don't know how to deal with dup code in scripts
import json
import requests
import sqlalchemy as db
from classes.lolparser import LolParser

def main():
    """ main function of get_champion_data

    """

    url = "http://ddragon.leagueoflegends.com/cdn/11.8.1/data/en_US/champion.json"

    # https://ddragon.leagueoflegends.com/api/versions.json -- versions
    res = requests.get(url)
    champ_res = json.loads(res.text)
    champ_data = champ_res['data']

    champ_table = db.Table('champions', LolParser.metadata,\
            autoload=True, autoload_with=LolParser.engine)

    # insert NONE with id of -1 in case someone didn't ban something.
    champ_table_insert = db.insert(champ_table).values(
            key=-1,
            id='NONE',
            name='NONE',
            title='NONE',
            blurb='NONE')

    LolParser.connection.execute(champ_table_insert)

    for champ in champ_data:
        print(champ_res['data'][champ])
        champ_table_insert = db.insert(champ_table).values(
                key=champ_res['data'][champ]['key'],
                id=champ_res['data'][champ]['id'],
                name=champ_res['data'][champ]['name'],
                title=champ_res['data'][champ]['title'],
                blurb=champ_res['data'][champ]['blurb'])

        LolParser.connection.execute(champ_table_insert)

main()
