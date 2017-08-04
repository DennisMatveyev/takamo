from core.logger import Logger

from core.config import configuration
from models import PostgresModel, RabbitModel
from resources import Connector


class Facade:
    """
    Facade pattern which includes all main initializations and calls
    """
    def start(self):
        Logger.setup_logger(filename=configuration.LOG_FILE)
        logger = Logger.get_logger()
        logger.info("Action Daemon started running.")

        db_conn, rabbit_conn = None, None

        try:
            # creating connection to Postgres and reading data
            db_conn = Connector().get_postgres_conn()
            actions_conn = PostgresModel(db_conn)
            actions = actions_conn.read()

            # creating connection to Rabbit and sending data
            rabbit_conn = Connector().get_rabbit_conn()
            rabbit = RabbitModel(rabbit_conn, actions)
            rabbit.send()

            logger.info("Action Daemon terminated normally.")
        except Exception as e:
            logger.error('Error: {}'.format(e))
        finally:
            if db_conn and rabbit_conn:
                db_conn.close()
                rabbit_conn.close()
