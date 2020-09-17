""" champ_table_setup

    This small script drops and creates the champions table in case we need to
    reset this table, or get new data from totally empty.

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
from sqlalchemy import Column, Table, Integer, String, MetaData # type: ignore
from classes.lolparser import LolParser

def main():
    """ main function of champ_table_setup import from LolParser and then creates the table

    """
    champs_table = Table('champions', LolParser.metadata,\
            autoload=True, autoload_with=LolParser.engine)

    champs_table.drop(LolParser.engine)

    champs_table = Table('champions',
            MetaData(),
            Column('key', Integer, primary_key=True),
            Column('id', String(30)),
            Column('name', String(30)),
            Column('title', String(50)),
            Column('blurb', String(400)))

    champs_table.create(LolParser.engine)

main()
