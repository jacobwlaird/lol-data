""" item_table_setup

    This small script drops and creates the items table in case we need to
    reset this table, or get new data from totally empty.

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
from sqlalchemy import Column, Table, Integer, String, MetaData
from classes.lolparser import LolParser

def main():
    """ main function of item_table_setup import from LolParser and then creates the table

    """
    # drop the champs table.

    items_table = Table('items', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
    items_table.drop(LolParser.engine)

    # create the champs table
    items_table = Table('items',\
            MetaData(),\
            Column('key', Integer, primary_key=True),\
            Column('name', String(40)))

    items_table.create(LolParser.engine)

main()
