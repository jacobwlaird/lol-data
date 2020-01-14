import json
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData
from classes.lolparser import LolParser

# drop the champs table.

champs_table = Table('champions', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
champs_table.drop(LolParser.engine)

# create the champs table
champs_table = Table('champions',
        MetaData(),
        Column('key', Integer, primary_key=True),
        Column('id', String(30)),
        Column('name', String(30)),
        Column('title', String(50)),
        Column('blurb', String(400)))

champs_table.create(LolParser.engine)
