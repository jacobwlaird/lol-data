""" data-base-setup-v2

    This script creates all of the tables in our database incase we needed to reset it, or if we
    need to create the db on a different sever or whatever.

"""
from classes.models import TeamData, MatchData, ScriptRuns, LeagueUsers, Champions, Items, JsonData
from classes.lolconfig import LolConfig
from classes.loldb import LolDB

def main():
    """ main function of data-base-setup-v2 creates all of the tables according to our
        model specifications.

    """

    config = LolConfig()
    our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)

    TeamData.__table__.create(bind=our_db.engine, checkfirst=True)
    MatchData.__table__.create(bind=our_db.engine, checkfirst=True)
    ScriptRuns.__table__.create(bind=our_db.engine, checkfirst=True)
    LeagueUsers.__table__.create(bind=our_db.engine, checkfirst=True)
    Champions.__table__.create(bind=our_db.engine, checkfirst=True)
    Items.__table__.create(bind=our_db.engine, checkfirst=True)
    JsonData.__table__.create(bind=our_db.engine, checkfirst=True)

if __name__ == "__main__":
    main()
