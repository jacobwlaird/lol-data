""" loldb.py class

This class has all the objects and properties we need to interact with our database. This should
only be used in lolparser.py and in scripts as needed.

"""

import sqlalchemy as db # type: ignore

#pylint: disable=too-many-instance-attributes # This should be fine for loldb.
#pylint: disable=too-few-public-methods # also fine for loldb.
#pylint: disable=C0103 # Session is an invalid name, but we're leaving it for now.
class LolDB():
    """ Contains all the methods and functions needed by loldata.py and lolaccount.py
        Attributes:

            engine        (obj): Sqlalchemy engine object created with config file contents
            connection    (obj): Sqlalchemy connection object created from the sqla engine
            metadata      (obj): Database metadata object

    """

    def __init__(self, host, user, pw, name):
        self.engine = db.create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(user,\
                pw, host, name), pool_size=100, max_overflow=100)

        self.connection = self.engine.connect()
        self.metadata = db.MetaData(bind=self.engine)
        self.metadata.reflect()

        Session = db.orm.sessionmaker(bind=self.engine)
        self.session = Session()
