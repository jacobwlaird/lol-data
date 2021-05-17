""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.

"""

import unittest
from classes import lolparser # pylint: disable=E0611

class TestLolParserGetFirstBloodKillAssist(unittest.TestCase):
    """ Contains all the test cases for get_first_blood_kill_assist().
    """

    def test_with_zeros(self):
        """ Tests with 0's as inputs.
        """

        data = {'firstBloodKill': 0, 'firstBloodAssist': 0}
        result = lolparser.LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_empty_dict(self):
        """ tests with an empty dictionary as input.
        """

        data = {}
        result = lolparser.LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_ones(self):
        """ tests with 1's as inputs.
        """

        data = {'firstBloodKill': 1, 'firstBloodAssist': 1}
        result = lolparser.LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 1))

    def test_with_strings(self):
        """ tests passing strings as the value of the key. This shouldn't happen,
            but we should make sure our function still works if it does.
        """

        data = {'firstBloodKill': '1', 'firstBloodAssist': '0'}
        result = lolparser.LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 0))

class TestLolParserGetPerks(unittest.TestCase):
    """ Contains all the test cases for get_perks().
    """
    def test_get_perks(self):
        """ tests with standard inputs
        """

        data = {"perk0": "0", "perk1": "1", "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = lolparser.LolParser.get_perks(data)

        self.assertEqual(result, "0, 1, 2, 3, 4, 5")

    def test_get_perks_with_missing_perks(self):
        """ tests with a missing perk. This shouldn't happen, but if it does it should be
            handeled.
        """

        data = {"perk0": "0",  "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = lolparser.LolParser.get_perks(data)

        self.assertEqual(result, "0, 2, 3, 4, 5")

class TestLolParserGetStartTimeAndDuration(unittest.TestCase):
    """ Contains all the test cases for get_start_time_and_duration().
    """
    def test_with_sub_hour_duration(self):
        """ tests with a duration of less than 60 minutes.
        """
        create_time = 1527560127149
        duration = 3599
        result = lolparser.LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "59:59"))

    def test_with_exactly_one_hour_duration(self):
        """ tests with a duration of exactly 60 minutes.
        """
        create_time = 1527560127149
        duration = 3600
        result = lolparser.LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:00:00"))

    def test_with_super_hour_duration(self):
        """ tests with a duration greater than 60 minutes
        """
        create_time = 1527560127149
        duration = 3660
        result = lolparser.LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:01:00"))

if __name__ == "__main__":
    unittest.main()
