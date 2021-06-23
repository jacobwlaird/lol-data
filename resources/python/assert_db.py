""" assert_db.py

Contains a class that inherits from unittest. This classes function is to assert that the data we
get back from our public apis matches exactly what is in our test database.

This is part of an 'e2e' 'test' that verifies that loldata.py gets the same exact data in test,
as it does in prod.

This step of the e2e test happens last, after the script has ran again.

"""
import sys
import json
import unittest
import requests
from classes.loldb import LolDB
from classes.lolconfig import LolConfig
from classes.models import TeamData, MatchData, ScriptRuns, JsonData

#pylint: disable=too-many-locals # This is okay.
#pylint: disable=too-many-statements # This is also okay.

class E2e(unittest.TestCase):
    """ ensures the loldata.py script works exactly as it does in current prod.

    """
    def test(self):
        """
            It does the thing.

        """
        config = LolConfig()

        our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)

        # get team data from prod
        my_team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data")
        ptd = json.loads(my_team_data.text)

        # get team data from test
        ttd = our_db.session.query(TeamData).order_by(TeamData.match_id.desc()).all()

        self.assertEqual(len(ptd), len(ttd))

        print("Checking team_data")
        for i, _ in enumerate(ptd):
            self.assertEqual(ptd[i]['match_id'], ttd[i].match_id)
            self.assertEqual(str(ptd[i]['game_version']), str(ttd[i].game_version))
            self.assertEqual(ptd[i]['win'], str(ttd[i].win))
            self.assertEqual(ptd[i]['participants'], str(ttd[i].participants))
            self.assertEqual(ptd[i]['first_blood'], str(ttd[i].first_blood))
            self.assertEqual(ptd[i]['first_baron'], str(ttd[i].first_baron))
            self.assertEqual(ptd[i]['first_tower'], str(ttd[i].first_tower))
            self.assertEqual(ptd[i]['first_dragon'], str(ttd[i].first_dragon))
            self.assertEqual(str(ptd[i]['first_inhib']), str(ttd[i].first_inhib))
            self.assertEqual(str(ptd[i]['first_rift_herald']), str(ttd[i].first_rift_herald))
            self.assertEqual(str(ptd[i]['ally_dragon_kills']), str(ttd[i].ally_dragon_kills))
            self.assertEqual(str(ptd[i]['ally_rift_herald_kills']),\
                    str(ttd[i].ally_rift_herald_kills))

            self.assertEqual(str(ptd[i]['enemy_dragon_kills']), str(ttd[i].enemy_dragon_kills))
            self.assertEqual(str(ptd[i]['enemy_rift_herald_kills']),\
                    str(ttd[i].enemy_rift_herald_kills))

            self.assertEqual(str(ptd[i]['inhib_kills']), str(ttd[i].inhib_kills))
            self.assertEqual(str(ptd[i]['bans']), str(ttd[i].bans))
            self.assertEqual(str(ptd[i]['enemy_bans']), str(ttd[i].enemy_bans))
            self.assertEqual(str(ptd[i]['allies']), str(ttd[i].allies))
            self.assertEqual(str(ptd[i]['enemies']), str(ttd[i].enemies))
            self.assertEqual(str(ptd[i]['start_time']), str(ttd[i].start_time))


        users = ['Spaynkee', 'Dumat', 'Archemlis', 'Stylus Crude', 'dantheninja6156', 'Csqward']
        for user in users:
            print(f"Checking match_data for {user}")
            pud = json.loads(requests.get(\
                f"http://paulzplace.asuscomm.com/api/get_user_data?name={user}").text)

            tud = our_db.session.query(MatchData).filter_by(player=user).order_by(\
                    MatchData.match_id.desc()).all()

            self.assertEqual(len(pud), len(tud))

            # add more fields
            for i, _ in enumerate(pud):
                self.assertEqual(str(pud[i]['match_id']), str(tud[i].match_id))
                self.assertEqual(str(pud[i]['player']), str(tud[i].player))
                self.assertEqual(str(pud[i]['role']), str(tud[i].role))
                self.assertEqual(str(pud[i]['champion']), str(tud[i].champion))
                self.assertEqual(str(pud[i]['champion_name']), str(tud[i].champion_name))
                self.assertEqual(str(pud[i]['enemy_champion']), str(tud[i].enemy_champion))

                self.assertEqual(str(pud[i]['enemy_champion_name']),\
                        str(tud[i].enemy_champion_name))

                self.assertEqual(str(pud[i]['first_blood']), str(tud[i].first_blood))
                self.assertEqual(str(pud[i]['first_blood_assist']), str(tud[i].first_blood_assist))
                self.assertEqual(str(pud[i]['kills']), str(tud[i].kills))
                self.assertEqual(str(pud[i]['assists']), str(tud[i].assists))
                self.assertEqual(str(pud[i]['deaths']), str(tud[i].deaths))
                self.assertEqual(str(pud[i]['damage_to_champs']), str(tud[i].damage_to_champs))
                self.assertEqual(str(pud[i]['damage_to_turrets']), str(tud[i].damage_to_turrets))
                # floats don't like to cooperate.
                if tud[i].gold_per_minute:
                    self.assertEqual(pud[i]['gold_per_minute'],\
                            f'{float(tud[i].gold_per_minute):g}')

                if tud[i].creeps_per_minute:
                    self.assertEqual(pud[i]['creeps_per_minute'],\
                            f'{float(tud[i].creeps_per_minute):g}')

                if tud[i].xp_per_minute:
                    self.assertEqual(pud[i]['xp_per_minute'], f'{float(tud[i].xp_per_minute):g}')

                self.assertEqual(str(pud[i]['wards_placed']), str(tud[i].wards_placed))

                self.assertEqual(str(pud[i]['vision_wards_bought']),\
                        str(tud[i].vision_wards_bought))

                self.assertEqual(str(pud[i]['wards_killed']), str(tud[i].wards_killed))
                self.assertEqual(str(pud[i]['items']), str(tud[i].items))
                self.assertEqual(str(pud[i]['perks']), str(tud[i].perks))


        print("Checking json_data")
        my_json_data = requests.get("http://paulzplace.asuscomm.com/api/get_json_data")

        pjd = json.loads(my_json_data.text)
        tjd = our_db.session.query(JsonData).all()

        self.assertEqual(len(pjd), len(tjd))

        for i, _ in enumerate(pjd):
            self.assertEqual(pjd[i]['match_id'], tjd[i].match_id)
            self.assertEqual(pjd[i]['json_data'], tjd[i].json_data)

        print("Checking Script Runs")
        my_runs_data = requests.get("http://paulzplace.asuscomm.com/api/get_script_runs")
        prd = json.loads(my_runs_data.text)


        trd = our_db.session.query(ScriptRuns).all()

        # the test db will have one more script run, the one that just happened.
        self.assertEqual(len(prd)+1, len(trd))

        for i, _ in enumerate(prd):
            self.assertEqual(prd[i]['id'], trd[i].id)
            self.assertEqual(prd[i]['source'], trd[i].source)
            self.assertEqual(prd[i]['status'], trd[i].status)
            self.assertEqual(prd[i]['matches_added'], trd[i].matches_added)


        # make sure our script run was recorded correctly.
        self.assertEqual(prd[-1]['id']+1, trd[-1].id)
        self.assertEqual("Test", trd[-1].source)
        self.assertEqual("Success", trd[-1].status)

if __name__ == "__main__":
    # If you're gonna remove this exit, you better be in test. or else.
    sys.exit()
    unittest.main()
