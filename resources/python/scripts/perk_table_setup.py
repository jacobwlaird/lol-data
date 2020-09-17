""" perks_table_setup

    This small script drops and creates the perks table in case we need to
    reset this table, or get new data from totally empty.

    Note: This, like all other scripts have to be ran from resources/python for now.

    Also, this table doesn't exist, but we have this script anyway, when it actually does.

"""
from sqlalchemy import Column, Table, Integer, String, MetaData
from classes.lolparser import LolParser

def main():
    """ main function of perks_table_setup import from LolParser and then creates the table

    """
    # drop the perks table
    perks_table = Table('perks', LolParser.metadata, autoload=True, autoload_with=LolParser.engine)
    perks_table.drop(LolParser.engine)

    # create the perks table
    perks_table = Table('perks',
            MetaData(),
            Column('key', Integer, primary_key=True),
            Column('name', String(40)))

    perks_table.create(LolParser.engine)

main()
