import logging


class Logger:
    """
    Simple class which store logger instance in itself.
    """
    logger = None

    @classmethod
    def get_logger(cls):
        if not cls.logger:
            cls.logger = cls.setup_logger()

        return cls.logger

    @classmethod
    def setup_logger(cls, logger_name="action_daemon", filename=None):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(format='%(asctime)s -[%(levelname)s] > %(message)s')

        if filename is not None:
            filehandler = logging.FileHandler(filename)
            formatter = logging.Formatter('%(asctime)s: %(message)s')
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
        return logger
