import requests
import json
import sqlalchemy as db
from classes.lolparser import LolParser

#Update the version number in the future if we need to.
url = "http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json"
res = requests.get(url)
champ_res = json.loads(res.text)
champ_data = champ_res['data']

champ_table = db.Table('champions', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

for champ in champ_data:
    print(champ_res['data'][champ])
    champ_table_insert = db.insert(champ_table).values(
            key=champ_res['data'][champ]['key'],
            id=champ_res['data'][champ]['id'],
            name=champ_res['data'][champ]['name'],
            title=champ_res['data'][champ]['title'],
            blurb=champ_res['data'][champ]['blurb'])

    results = LolParser.connection.execute(champ_table_insert)


