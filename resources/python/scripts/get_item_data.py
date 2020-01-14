import requests
import json
import sqlalchemy as db
from classes.lolparser import LolParser

#Update the version number in the future if we need to.
url = "http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/item.json"
res = requests.get(url)
item_res = json.loads(res.text)
item_data = item_res['data']

item_table = db.Table('items', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

for item in item_data:
    item_table_insert = db.insert(item_table).values(
            key=item,
            name=item_res['data'][item]['name'])

    results = LolParser.connection.execute(item_table_insert)


