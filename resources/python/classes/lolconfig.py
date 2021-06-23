""" lolconfig.py

    This class does everything needed to read a config file and store some values for use in
    the other classes.

"""
import configparser

#pylint: disable=too-few-public-methods # This is fine for lolconfig.
class LolConfig():
    """ Contains all the methods and functions needed by loldata.py and lolaccount.py
        Attributes:

            _config         (obj): ConfigParser object for reading config file

            db_host        (str): database host address from config file
            db_user        (str): database user from config file
            db_pw          (str): database user password from config file
            db_name        (str): database name from config file
            api_key        (str): riot games permanent api key

            log_file_name (str): Log file name pulled from config file
            logger        (obj): Log object that we call to, to log

    """

    def __init__(self, file_name=None):
        if not file_name:
            file_name = './resources/python/general.cfg'

        #pylint: disable=no-value-for-parameter # this is a false positive?
        self._config = configparser.ConfigParser()
        self._config.read(file_name)

        self.db_host = self._config.get('DATABASE', 'db_id')
        self.db_user = self._config.get('DATABASE', 'db_user')
        self.db_pw = self._config.get('DATABASE', 'db_password')
        self.db_name = self._config.get('DATABASE', 'db_name')

        self.api_key = self._config.get('RIOT', 'api_key')
        self.log_file_name = self._config.get('LOGGING', 'file_name')
