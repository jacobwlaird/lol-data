""" json_table_setup

    This small script drops and creates the json_data table in case we need to
    reset this table, or get new data from totally empty.

    Note: This, like all other scripts have to be ran from resources/python for now.

"""
from sqlalchemy import Column, Table, BigInteger, MetaData, Text
from classes.lolparser import LolParser

def main():
    """ main function of json_table_setup import from LolParser and then creates the table

    """
    # drop the json table
    try:
        json_table = Table('json_data', LolParser.metadata,\
                autoload=True, autoload_with=LolParser.engine)
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

main()
