""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.


Don't forget -- Run this from the root folder /lol-data and use the command
python -m unittest resources.python.test.unit.test_lolparser
"""

import unittest
import json
from collections import defaultdict
from unittest.mock import Mock, MagicMock
from resources.python.classes.lolparser import LolParser

class TestLolParserGetFirstBloodKillAssist(unittest.TestCase):
    """ Contains all the test cases for get_first_blood_kill_assist().
    """

    def test_with_zeros(self):
        """ Tests with 0's as inputs.
        """

        data = {'firstBloodKill': 0, 'firstBloodAssist': 0}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_empty_dict(self):
        """ tests with an empty dictionary as input.
        """

        data = {}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_ones(self):
        """ tests with 1's as inputs.
        """

        data = {'firstBloodKill': 1, 'firstBloodAssist': 1}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 1))

    def test_with_strings(self):
        """ tests passing strings as the value of the key. This shouldn't happen,
            but we should make sure our function still works if it does.
        """

        data = {'firstBloodKill': '1', 'firstBloodAssist': '0'}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 0))

class TestLolParserGetPerks(unittest.TestCase):
    """ Contains all the test cases for get_perks().
    """
    def test_get_perks(self):
        """ tests with standard inputs
        """

        data = {"perk0": "0", "perk1": "1", "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = LolParser.get_perks(data)

        self.assertEqual(result, "0, 1, 2, 3, 4, 5")

    def test_get_perks_with_missing_perks(self):
        """ tests with a missing perk. This shouldn't happen, but if it does it should be
            handeled.
        """

        data = {"perk0": "0",  "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = LolParser.get_perks(data)

        self.assertEqual(result, "0, 2, 3, 4, 5")

class TestLolParserGetStartTimeAndDuration(unittest.TestCase):
    """ Contains all the test cases for get_start_time_and_duration().
    """
    def test_with_sub_hour_duration(self):
        """ tests with a duration of less than 60 minutes.
        """
        create_time = 1527560127149
        duration = 3599
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "59:59"))

    def test_with_exactly_one_hour_duration(self):
        """ tests with a duration of exactly 60 minutes.
        """
        create_time = 1527560127149
        duration = 3600
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:00:00"))

    def test_with_super_hour_duration(self):
        """ tests with a duration greater than 60 minutes
        """
        create_time = 1527560127149
        duration = 3660
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:01:00"))

class TestLolParserSelectPreviousTeamDataRows(unittest.TestCase):
    """ Contains all the test cases for select_previous_team_data_rows
    """

    @staticmethod
    def test_function_calls():
        """ Asserts that query() and all() get called exactly once."""

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        parser.select_previous_team_data_rows()

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().all.assert_called_once()

class TestLolParserSelectPreviousMatchDataRows(unittest.TestCase):
    """ Contains all the test cases for select_previous_match_data_rows
    """

    @staticmethod
    def test_function_calls():
        """ Asserts that query(), all(), and filter_by() get called exactly once."""

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        # Do I use an actual string here? What to do...
        parser.select_previous_match_data_rows(Mock())

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().filter_by.assert_called_once()
        mock_db_class.session.query().filter_by().all.assert_called_once()

class TestLolParserGetPreviousTeamDataMatchIds(unittest.TestCase):
    """ Contains all the test cases for get_previous_team_data_match_ids
    """

    def test_with_match_ids(self):
        """ If given a list of objects match_ids, a list of ints gets returned """

        mock_select_previous_team_data = MagicMock()
        mock_previous_team_data = []

        mock_first_row = Mock()
        mock_first_row.match_id = 111
        mock_previous_team_data.append(mock_first_row)

        mock_second_row = Mock()
        mock_second_row.match_id = 222
        mock_previous_team_data.append(mock_second_row)

        mock_third_row = Mock()
        mock_third_row.match_id = 333
        mock_previous_team_data.append(mock_third_row)

        mock_select_previous_team_data.return_value = mock_previous_team_data

        parser = LolParser()
        parser.select_previous_team_data_rows = mock_select_previous_team_data

        result = parser.get_previous_team_data_match_ids()
        mock_select_previous_team_data.assert_called_once()
        self.assertEqual(result, [111, 222, 333])
        self.assertEqual(type(result[0]), int)

class TestLolParserGetPreviousPlayerMatchDataIds(unittest.TestCase):
    """ Contains all the test cases for get_previous_player_match_data_ids
    """

    def test_with_ids(self):
        """ If given a list of objects match_ids, a list of ints gets returned """

        mock_select_previous_match_data_rows = MagicMock()
        mock_previous_match_data = []

        mock_first_row = Mock()
        mock_first_row.match_id = 111
        mock_previous_match_data.append(mock_first_row)

        mock_second_row = Mock()
        mock_second_row.match_id = 222
        mock_previous_match_data.append(mock_second_row)

        mock_third_row = Mock()
        mock_third_row.match_id = 333
        mock_previous_match_data.append(mock_third_row)

        mock_select_previous_match_data_rows.return_value = mock_previous_match_data

        parser = LolParser()
        parser.select_previous_match_data_rows = mock_select_previous_match_data_rows

        result = parser.get_previous_player_match_data_ids(Mock())
        mock_select_previous_match_data_rows.assert_called_once()

        self.assertEqual(result, [111, 222, 333])
        self.assertEqual(type(result[0]), int)

class TestLolParserInsertMatchDataRow(unittest.TestCase):
    """ Contains all the test cases for insert_match_data_row
    """

    def test_number_of_function_calls(self):
        """ tests that the number of functions called is exactly what we expected."""
        
        mock_dict = MagicMock()
        mock_db = MagicMock()

        # mock function calls.
        mock_get_participant_index = MagicMock()
        mock_get_champ_name = MagicMock()
        mock_get_first_blood_kill_assist = MagicMock(return_value=[None,None])
        mock_get_role = MagicMock()
        mock_get_gold_cs_xp_delta = MagicMock(return_value=[None, None, None])
        mock_get_enemy_champion = MagicMock()
        mock_get_perks = MagicMock()
        mock_get_items = MagicMock()


        parser = LolParser()

        parser.our_db = mock_db
        parser.get_participant_index = mock_get_participant_index
        parser.get_champ_name = mock_get_champ_name
        parser.get_first_blood_kill_assist = mock_get_first_blood_kill_assist
        parser.get_role = mock_get_role
        parser.get_gold_cs_xp_delta = mock_get_gold_cs_xp_delta
        parser.get_enemy_champ = mock_get_enemy_champion
        parser.get_perks = mock_get_perks
        parser.get_items = mock_get_items

        parser.insert_match_data_row(mock_dict, "test", Mock())

        # make sure our functions are called the correct number of times.
        mock_db.session.add.assert_called_once()
        mock_get_participant_index.assert_called_once()
        self.assertEqual(mock_get_champ_name.call_count, 2)
        mock_get_first_blood_kill_assist.assert_called_once()
        mock_get_role.assert_called_once()
        mock_get_gold_cs_xp_delta.assert_called_once()
        mock_get_enemy_champion.assert_called_once()
        mock_get_perks.assert_called_once()
        mock_get_items.assert_called_once()



class TestLolParserInsertTeamDataRow(unittest.TestCase):
    """ Contains all the test cases for insert_team_data_row
    """

    def test_number_of_function_calls(self):
        """ tests that the number of functions called is exactly what we expected."""
        mock_dict = MagicMock()
        mock_db = MagicMock()

        # mock function calls.
        mock_get_team_data = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_get_team_bans = MagicMock()
        mock_get_allies_and_enemies = MagicMock(return_value=[None, None])
        mock_get_start_time_and_duration = MagicMock(return_value=[None, None])


        parser = LolParser()

        parser.our_db = mock_db
        parser.get_team_data = mock_get_team_data
        parser.get_team_bans = mock_get_team_bans
        parser.get_allies_and_enemies = mock_get_allies_and_enemies
        parser.get_start_time_and_duration = mock_get_start_time_and_duration

        parser.insert_team_data_row(mock_dict, "test", Mock())

        mock_db.session.add.assert_called_once()
        mock_get_team_data.assert_called_once()
        self.assertEqual(mock_get_team_bans.call_count, 2)
        mock_get_allies_and_enemies.assert_called_once()
        mock_get_start_time_and_duration.assert_called_once()

    def test_with_data(self):
        """ tests that data is parsed correctly. 

            This is a somewhat weird test, as it doesn't test anything returned by other functions
            function. This is somewhat by design as this is a unit test, and I'll have the same
            test but more robust as an integration test.

            I may still remove this test at some point after I write the integration test.
        """

        test_file = open("resources/python/test/test_statics/1", "r")
        match_dict = json.loads(test_file.read())

        mock_db = MagicMock()

        parser = LolParser()

        parser.our_db = mock_db

        parser.insert_team_data_row(match_dict, "Spaynkee",\
                "OIesQl3aYp9Mlfi7OgKFXp1i2brmVO0QUMSE0adgol7L2g")

        team_data_obj = mock_db.session.add.call_args.args[0]

        self.assertEqual(team_data_obj.participants, "Spaynkee")
        self.assertEqual(team_data_obj.win, "Fail")
        self.assertEqual(team_data_obj.first_blood, 0)
        self.assertEqual(team_data_obj.first_baron, 0)
        self.assertEqual(team_data_obj.first_tower, 0)
        self.assertEqual(team_data_obj.first_rift_herald, 0)
        self.assertEqual(team_data_obj.ally_rift_herald_kills, 0)
        self.assertEqual(team_data_obj.first_dragon, 0)
        self.assertEqual(team_data_obj.ally_dragon_kills, 2)
        self.assertEqual(team_data_obj.first_inhib, 0)
        self.assertEqual(team_data_obj.inhib_kills, 0)
        self.assertEqual(team_data_obj.game_version, '11.13.382.1241')
        self.assertEqual(team_data_obj.match_id, 3959945080)
        self.assertEqual(team_data_obj.enemy_dragon_kills, 4)
        self.assertEqual(team_data_obj.enemy_rift_herald_kills, 2)

        test_file.close()

if __name__ == "__main__":
    unittest.main()
