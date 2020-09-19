""" runs_table_setup

    This small script drops and creates the script_runs table in case we need to
    reset this table, or get new data from totally empty.

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
#pylint: skip-file # I don't want to do this, but I don't know how to deal with dup code in scripts
from sqlalchemy import Column, Table, Integer, String, TIMESTAMP, MetaData
from classes.lolparser import LolParser
def main():
    """ main function of runs_table_setup import from LolParser and then creates the table

    """

    # drop the runs table
    runs_table = Table('script_runs', LolParser.metadata, autoload=True,\
            autoload_with=LolParser.engine)
    runs_table.drop(LolParser.engine)

    # create the runs table
    runs_table = Table('script_runs',\
            MetaData(),\
            Column('id', Integer, primary_key=True, autoincrement=True),\
            Column('source', String(50)),\
            Column('status', String(20)),\
            Column('matches_added', String(60000)),\
            Column('start_time', TIMESTAMP),\
            Column('end_time', TIMESTAMP),\
            Column('message', String(1000))\
            )

    runs_table.create(LolParser.engine)
