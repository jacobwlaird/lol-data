import json
import os
import os.path
import time
from sqlalchemy import Column, Table, Integer, String, BigInteger, Boolean, Float, TIMESTAMP, Time, MetaData
from classes.lolparser import LolParser

# drop the runs table 
runs_table = Table('script_runs', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
runs_table.drop(LolParser.engine)

# create the runs table
runs_table = Table('script_runs',
        MetaData(),
        Column('id', Integer, primary_key=True, autoincrement=True), 
        Column('source', String(50)),
        Column('status', String(20)),
        Column('matches_added', String(60000)), # so this is a large max but idk how else to do it.
        Column('start_time', TIMESTAMP), 
        Column('end_time', TIMESTAMP), 
        Column('message', String(1000)) # so this is a large max but idk how else to do it.
        )

runs_table.create(LolParser.engine)
