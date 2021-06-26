"""correct_notfound_items.py

This script is meant to cleanup any 'NOT FOUND' items that make their
way into the items table for each match. It makes get queries to the sql database
and at the end a single update.

"""

import json
import configparser
import mysql.connector


config = configparser.ConfigParser()
config.read("general.cfg")
mydb = mysql.connector.connect(
    host=config["DATABASE"]["db_id"],
    user=config["DATABASE"]["db_user"],
    password=config["DATABASE"]["db_password"],
    database=config["DATABASE"]["db_name"],
)
mycursor = mydb.cursor()


def get_match_info():
    """ Retrievs list of summoner name, match ID, and record ID from match_data table
        for every found match that requires repairing. Will return a tuple with
        match_id, summoner name, and record ID of match from the matches table.
    """
    mycursor.execute("SELECT match_id, player, id FROM match_data WHERE items LIKE '%NOT FOUND%'")
    myresult = mycursor.fetchall()

    return myresult


def get_items_from_json(m_id, summoner):
    """ This query gives us the json data for a match

        Args:
            m_id: a match id to retrieve data from.
            summoner: primary summoner name of the match
    """
    sql = f"SELECT json_data FROM json_data WHERE match_id='{m_id}'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    if myresult == []:
        print(f"Could not find json data for {m_id}. Skipping")
        return 0

    dic = json.loads(myresult[0][0])
    ids = dic["participantIdentities"]

    part_id = 0
    for i in ids:
        if i["player"]["summonerName"].lower() == summoner.lower():
            part_id = i["participantId"]

    items = []
    for participant in dic["participants"]:
        if participant["participantId"] == part_id:
            items.append(participant["stats"]["item0"])
            items.append(participant["stats"]["item1"])
            items.append(participant["stats"]["item2"])
            items.append(participant["stats"]["item3"])
            items.append(participant["stats"]["item4"])
            items.append(participant["stats"]["item5"])
            items.append(participant["stats"]["item6"])

    return items


def get_item_names(items):
    """Retrieve the item IDs, looks up their names, creates a string.

        Args:
        items: a list item IDs
    """
    item_names = []
    for i in items:
        if i == 0:
            continue
        sql = f"SELECT `name` FROM items WHERE `key`={i}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        item_names.append(myresult[0][0])

    item_string = ", ".join(item_names)
    item_string = item_string.replace("'", "''")
    return item_string


def update_record(item_string, table_id):
    """Insert updated string
        Args:
        item_string: a string with all the items from that player for that match
        table_id: the record to update
    """
    sql = f"UPDATE match_data SET items = '{item_string}' WHERE id='{table_id}'"
    mycursor.execute(sql)
    mydb.commit()


if __name__ == "__main__":
    data = get_match_info()

    MATCH_COUNT = len(data)
    print(f"Found {MATCH_COUNT} matches.")
    PROGRESS_COUNT = 1
    # 0 is match id, 1 is summoner name, 2 is table ID
    for datum in data:
        item_list = get_items_from_json(datum[0], datum[1])
        if item_list == 0:
            continue
        NEW_ITEM_STRING = get_item_names(item_list)
        print(
            f"{PROGRESS_COUNT} of {MATCH_COUNT}."
            f" Adding {NEW_ITEM_STRING} to match {datum[0]} on record {datum[2]}"
        )
        PROGRESS_COUNT += 1
        update_record(NEW_ITEM_STRING, datum[2])
