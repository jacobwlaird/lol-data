""" update_static_data.py

    This script hits a few public apis containing data for specific patches of league of legends
    In particular, this script gets champion and item data.

"""

import json
import requests
from classes.lolconfig import LolConfig
from classes.loldb import LolDB
from classes.models import Champions, Items

#pylint: disable=C0103 # columns are named id, which makes the linter angry.
#pylint: disable=W0622 # columns are named id, which makes the linter angry.
def main():
    """ main function of update_static_data.py

        This functions gets the latest patches static data and stores it into the db.
        By default, it should only run for the latest patch.

        It's possible to get data for multiple patches if you create a versions list
        and pass that to the functions as well.

        ex: ["3.11.2", "3.9.4","3.12.37"] etc.

    """

    config = LolConfig()
    our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)

    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    version_res = requests.get(version_url)
    versions = json.loads(version_res.text)

    latest_version = versions[0]

    store_champion_data([latest_version], our_db)
    store_item_data([latest_version], our_db)
    #store_item_data(versions, our_db) # If you want every item ever.


def store_champion_data(versions: list, our_db: object):
    """ Gets and processes json data about champions from riot games.

        Args:
            versions: a list of versions we're getting data for. This is usually the latest version
            our_db: An instance of the LolDB class so that we can actually store the data.

    """
    for version in versions:
        print(f"Getting champion data for patch {version}")
        champs_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        res = requests.get(champs_url)
        champ_res = json.loads(res.text)
        champ_data = champ_res['data']


        for champ in champ_data:
            key = champ_res['data'][champ]['key']

            champ_check = our_db.session.query(Champions).filter(Champions.key==key).first()
            if champ_check:
                # Champion is already in the table, so we can skip it.
                continue

            id = champ_res['data'][champ]['id']
            name = champ_res['data'][champ]['name']
            title = champ_res['data'][champ]['title']
            blurb = champ_res['data'][champ]['blurb']

            champ_obj = Champions(key, id, name, title, blurb)
            our_db.session.add(champ_obj)

        our_db.session.commit()

def store_item_data(versions: list, our_db: object):
    """ Gets and processes json data about items from riot games.

        Args:
            versions: a list of versions we're getting data for. This is usually the latest version
            our_db: An instance of the LolDB class so that we can actually store the data.

    """
    for version in versions:
        print(f"Getting item data for patch {version}")
        items_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
        res = requests.get(items_url)
        item_res = json.loads(res.text)
        item_data = item_res['data']

        for item in item_data:
            item_check = our_db.session.query(Items).filter(Items.key==item).first()
            if item_check:
                continue

            item_obj = Items(item, item_res['data'][item]['name'])
            our_db.session.add(item_obj)

        our_db.session.commit()

if __name__ == "__main__":
    main()
