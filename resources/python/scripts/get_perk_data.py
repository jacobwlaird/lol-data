import requests
import json
import sqlalchemy as db
from classes.lolparser import LolParser

#Update the version number in the future if we need to. Maybe find a way to get most recent version? or...
url = "http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/perk.json"
res = requests.get(url)
perk_res = json.loads(res.text)
perk_data = perk_res['data']

perk_table = db.Table('perks', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

for perk in perk_data:
    perk_table_insert = db.insert(perk_table).values(
            key=perk,
            name=perk_res['data'][perk]['name'])

    results = LolParser.connection.execute(perk_table_insert)


