import json
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData
from classes.lolparser import LolParser

# drop the json table 
json_table = Table('json_data', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
json_table.drop(LolParser.engine)

# create the json table
json_table = Table('json_data',
        MetaData(),
        Column('match_id', BigInteger, primary_key=True),
        Column('json_data', varchar(max)))

json_table.create(LolParser.engine)
