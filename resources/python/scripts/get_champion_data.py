import requests
import json
import sqlalchemy as db
from classes.lolparser import LolParser

#Update the version number in the future if we need to.
url = "http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json"
res = requests.get(url)
champ_res = json.loads(res.text)
champ_data = champ_res['data']

champ_table = db.Table('champions', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)

# insert NONE with id of -1 in case someone didn't ban something.
champ_table_insert = db.insert(champ_table).values(
        key=-1,
        id='NONE',
        name='NONE',
        title='NONE',
        blurb='NONE')

results = LolParser.connection.execute(champ_table_insert)

for champ in champ_data:
    print(champ_res['data'][champ])
    champ_table_insert = db.insert(champ_table).values(
            key=champ_res['data'][champ]['key'],
            id=champ_res['data'][champ]['id'],
            name=champ_res['data'][champ]['name'],
            title=champ_res['data'][champ]['title'],
            blurb=champ_res['data'][champ]['blurb'])

    results = LolParser.connection.execute(champ_table_insert)


