""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.


Don't forget -- Run this from the root folder /lol-data and use the command
python -m unittest discover resources/python/test

"""

import unittest
import json
from collections import defaultdict
from unittest.mock import Mock, MagicMock, patch
from resources.python.classes.lolgather import LolGather

class TestLolGatherGetMatchReferenceDto(unittest.TestCase):
    """ Contains all the test cases for get_match_reference_dto().
    """

    @patch('requests.get')
    @patch('json.loads')
    def test_max_game_index_default(self, mock_requests, mock_json):
        """ Tests that our function works with max_game_index = 200
        """

        gather = LolGather()
        gather.get_match_reference_dto("1")
        self.assertEqual(mock_requests.call_count, 2)

    @patch('requests.get')
    @patch('json.loads')
    def test_max_game_index_fifty(self, mock_requests, mock_json):
        """ Tests that our function works with max_game_index = 50
        """

        gather = LolGather(50)
        gather.get_match_reference_dto("1")
        self.assertEqual(mock_requests.call_count, 1)

    @patch('requests.get')
    @patch('json.loads')
    def test_max_game_index_one_thousand(self, mock_requests, mock_json):
        """ Tests that our function works with max_game_index = 1000
        """

        gather = LolGather(1000)
        gather.get_match_reference_dto("1")
        self.assertEqual(mock_requests.call_count, 10)

if __name__ == "__main__":
    unittest.main()
