""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.

"""

import unittest
from collections import defaultdict
from unittest.mock import Mock, MagicMock
from ...classes.lolparser import LolParser

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
    """ Contains all the test cases for get_previous_player_match_data_ids
    """

    def create_match_data(self):
        # so I guess we would just hard set every peice of data taht we need for this function?
        # moving this somewhere else might be a bit neater, idk.

        something = {}
        something['gameId'] = 3
        return something

    def test_with_data(self):
        """ tests that the data is parsed correctly. """

        # Uhhh. What do to here?
        # well, we take a huge dict
        # I can make a mock object and set every param?
        # maybe I make a function that would return a ton of stock info to populate
        # the data?

        mock_dict = MagicMock()
        mock_dict.configure_mock(gameId=3)

        mock_db = MagicMock()
        mock_get_participant_index = MagicMock()

        parser = LolParser()

        parser.our_db = mock_db
        parser.get_participant_index = mock_get_participant_index

        parser.insert_match_data_row(mock_dict, "test", Mock())

        mock_get_participant_index.assert_called_once()
        mock_db.session.add.assert_called_once()
        match_data_obj = mock_db.session.add.call_args.args[0]

        self.assertEqual(match_data_obj.player, "test")

if __name__ == "__main__":
    unittest.main()
