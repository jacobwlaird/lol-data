""" loldb.py class

This class has all the objects and properties we need to interact with our database. This should
only be used in lolparser.py and in scripts as needed.

"""
import sqlalchemy as db # type: ignore

from .models import TeamData

#pylint: disable=too-many-instance-attributes # This should be fine for loldb.
#pylint: disable=too-few-public-methods # also fine for loldb.
#pylint: disable=C0103 # Session is an invalid name, but we're leaving it for now.
class LolDB():
    """ Contains all the methods and functions needed by loldata.py and lolaccount.py
        Attributes:

            engine        (obj): Sqlalchemy engine object created with config file contents
            connection    (obj): Sqlalchemy connection object created from the sqla engine
            metadata      (obj): Database metadata object

            champs_table     (obj): Sqlalchemy Table object for the champions table
            match_data_table (obj): Sqlalchemy Table object for the match_data table
            team_data_table  (obj): Sqlalchemy Table object for the team_data table
            items_table      (obj): Sqlalchemy Table object for the items table
            json_data_table  (obj): Sqlalchemy Table object for the json_data table
            runs_table       (obj): Sqlalchemy Table object for the script_runs table

    """

    def __init__(self, host, user, pw, name):
        self.engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(user,\
                pw, host, name), pool_size=100, max_overflow=100)

        # what do I do to associate the models with this?

        self.connection = self.engine.connect()
        self.metadata = db.MetaData(bind=self.engine)
        self.metadata.reflect()

        self.team_data = TeamData

        Session = db.orm.sessionmaker(bind=self.engine)
        self.session = Session()
