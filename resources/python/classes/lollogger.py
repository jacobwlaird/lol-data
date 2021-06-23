""" lollogger.py

    This python file contains all the logging functions we'll use in this project. It's pretty
    barren right now, as we're simple calling the logger object from other classes at the
    moment, to do all of our logging.

"""
import logging

#pylint: disable=too-few-public-methods # This is fine.
class LolLogger():
    """ Contains all the methods used to log to our log file.
        Attributes:

            log_file_name (str): Log file name pulled from config file
            logger        (obj): Log object that we call to, to log a message.

    """

    def __init__(self, file_name=None):
        #pylint: disable=no-value-for-parameter # this is a false positive?
        self.log_file_name = file_name

        logging.basicConfig(filename=self.log_file_name, level=logging.DEBUG)

        self.logger = logging.getLogger()

    def log_info(self, message: str):
        """ Logs an info message.

            Args:
                message: the message to be stored.
        """
        self.logger.info(message)

    def log_warning(self, message: str):
        """ Logs a warning message.

            Args:
                message: the message to be stored.
        """
        self.logger.warning(message)

    def log_error(self, message: str):
        """ Logs an error message.

            Args:
                message: the message to be stored.
        """
        self.logger.error(message)

    def log_critical(self, message: str):
        """ Logs an critical message. uh oh.

            Args:
                message: the message to be stored.
        """
        self.logger.critical(message)
