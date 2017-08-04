import pika
import psycopg2
from core.logger import Logger

from core.config import configuration

logger = Logger.get_logger()


class Connector:
    def get_postgres_conn(self):
        try:
            return psycopg2.connect(configuration.POSTGRES_LINK)
        except Exception as e:
            logger.error("Unable to connect to the Postgres: {}".format(e))

    def get_rabbit_conn(self):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=configuration.RABBIT_MQ_HOST))
        except Exception as e:
            logger.error("Unable to connect to the Rabbit: {}".format(e))
