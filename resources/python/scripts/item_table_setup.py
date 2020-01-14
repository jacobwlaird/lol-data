import json
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData
from classes.lolparser import LolParser

# drop the champs table.

items_table = Table('items', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
items_table.drop(LolParser.engine)

# create the champs table
items_table = Table('items',
        MetaData(),
        Column('key', Integer, primary_key=True),
        Column('name', String(40)))

items_table.create(LolParser.engine)
