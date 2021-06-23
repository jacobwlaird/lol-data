""" remove_last_data.py

This class removes a number of rows from the data copied by update_db_from_api.py

The intent is to make sure that loldata.py actually copies the same exact data that currently
exists in prod.

To that end, this portion of the 'e2e' 'test' removes some data prior to running loldata.py.

"""
import sys
import unittest
from classes.loldb import LolDB
from classes.lolconfig import LolConfig
from classes.models import TeamData, MatchData, JsonData

class RemoveDB(unittest.TestCase):
    """
        This class removes some amount of data from the database, then ensures it's actually gone.

    """

    def test_after_removing(self):
        """
            I'm not saying it again.

        """
        config = LolConfig()
        our_db = LolDB(config.db_host, config.db_user, config.db_pw,\
                config.db_name)

        matches_to_remove = []

        #getting pre-run data for asserts later.
        pre_team_data = our_db.session.query(TeamData).all()
        pre_match_data = our_db.session.query(MatchData).all()
        pre_json_data = our_db.session.query(JsonData).all()

        existing_match_history = our_db.session.query(TeamData).order_by(TeamData.match_id.desc())
        matches_to_remove = existing_match_history[:20]

        print(f"Removing these matches: {[match.match_id for match in matches_to_remove]}")

        # remove all participants in these matches from match_data
        num_matches_removed = 0
        for match in matches_to_remove:
            for particip in match.participants.split(","):
                print(f"Removing {match.match_id} From {particip.strip()}")
                our_db.session.query(MatchData).filter_by(match_id=match.match_id).filter_by(\
                        player=particip.strip()).delete()
                num_matches_removed += 1


        # then removes all these matches from the team_data and json_data tables.
        for match in matches_to_remove:
            our_db.session.query(JsonData).filter_by(match_id=match.match_id).delete()
            our_db.session.query(TeamData).filter_by(match_id=match.match_id).delete()

        our_db.session.commit()

        # asserts we only removed what we wanted to.
        current_team_data = our_db.session.query(TeamData).order_by(TeamData.match_id.desc()).all()
        current_match_data = our_db.session.query(MatchData).all()
        current_json_data = our_db.session.query(JsonData).all()

        # asserting we removed exactly 20 rows from team_data
        self.assertEqual(len(pre_team_data)-20, len(current_team_data))
        self.assertEqual(len(pre_match_data)-num_matches_removed, len(current_match_data))
        self.assertEqual(len(pre_json_data)-20, len(current_json_data))

        print("Running data collection script")

if __name__ == "__main__":
    # If you're gonna remove this exit, you better be in test. or else.
    sys.exit()
    unittest.main()
