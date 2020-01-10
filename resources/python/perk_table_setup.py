import json
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData
from classes.lolparser import LolParser

# drop the perks table 
perks_table = Table('perks', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
perks_table.drop(LolParser.engine)

# create the perks table
perks_table = Table('perks',
        MetaData(),
        Column('key', Integer, primary_key=True),
        Column('name', String(40)))

perks_table.create(LolParser.engine)
