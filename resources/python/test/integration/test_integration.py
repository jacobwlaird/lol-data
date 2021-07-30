import unittest
import json
from collections import defaultdict
from unittest.mock import Mock, MagicMock
from resources.python.classes.lolparser import LolParser

class TestTeamDataInserted(unittest.TestCase):
    """ Contains all the test cases for inserting team data.
    """

    def setUp(self):
        # I guess we need to create a database, and maybe the tables too?
        # would it be better to just run my other python scripts?
        # or.. I guess import the models.
        pass

    def test_with_data(self):
        """ tests that data is parsed correctly. 
            
            This will test that we parse data out correctly, assuming we can get data from
            riot.

            This will test several things, including our parser function, all the functions in the
            parser, and storing data into the database?
        """

        test_file = open("resources/python/test/test_statics/1", "r")
        match_dict = json.loads(test_file.read())
        
        # ah, now we don't want to mock this much anymore methinks.

        mock_db = MagicMock()
        mock_get_participant_index = MagicMock()
        mock_get_participant_index.return_value = 2

        parser = LolParser()

        parser.our_db = mock_db
        parser.get_participant_index = mock_get_participant_index

        parser.insert_match_data_row(match_dict, "Spaynkee",\
                "OIesQl3aYp9Mlfi7OgKFXp1i2brmVO0QUMSE0adgol7L2g")

        match_data_obj = mock_db.session.add.call_args.args[0]

        self.assertEqual(match_data_obj.player, "Spaynkee")
        self.assertEqual(match_data_obj.match_id, 3959945080)
        self.assertEqual(match_data_obj.role, "JUNGLE")
        self.assertEqual(match_data_obj.champion, 9)
        self.assertEqual(match_data_obj.first_blood, 0)
        self.assertEqual(match_data_obj.first_blood_assist, 0)
        self.assertEqual(match_data_obj.kills, 5)
        self.assertEqual(match_data_obj.deaths, 12)
        self.assertEqual(match_data_obj.assists, 20)
        self.assertEqual(match_data_obj.damage_to_champs, 24972)
        self.assertEqual(match_data_obj.damage_to_turrets, 0)
        self.assertEqual(match_data_obj.gold_per_minute, 274.125)
        self.assertEqual(match_data_obj.creeps_per_minute, 0.9)
        self.assertEqual(match_data_obj.xp_per_minute, 415.225)
        self.assertEqual(match_data_obj.wards_placed, 6)
        self.assertEqual(match_data_obj.vision_wards_bought, 7)
        self.assertEqual(match_data_obj.wards_killed, 6)

        test_file.close()
    def test_with_zeros(self):
        """ Tests with 0's as inputs.
        """

        data = {'firstBloodKill': 0, 'firstBloodAssist': 0}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

