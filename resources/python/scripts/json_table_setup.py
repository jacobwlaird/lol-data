import json
import os
import os.path
import time
from sqlalchemy import Column, Table, BigInteger, MetaData, Text
from classes.lolparser import LolParser

# drop the json table 
try:
    json_table = Table('json_data', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
    json_table.drop(LolParser.engine)
except:
    print("Json table didn't exist, probably, so we'll just create it now")
    

# create the json table
try:
    json_table = Table('json_data',
            MetaData(),
            Column('match_id', BigInteger, primary_key=True),
            Column('json_data', Text))

    json_table.create(LolParser.engine)
except Exception as e:
    print(e)
    print("Create json_data failed, better figure out why.")
