import unittest
from unittest.mock import MagicMock, patch

from core.config import configuration
from resources import Connector
from core.logger import Logger


class TestConnector(unittest.TestCase):
    def setUp(self):
        self.logger = Logger.get_logger()
        self.connector = Connector()

    def test_get_postgres_conn_success(self):
        mocked_connect = MagicMock()
        mocked_connect.return_value = 'test'

        with patch('psycopg2.connect', mocked_connect):
            result = self.connector.get_postgres_conn()
            mocked_connect.assert_called_once_with(configuration.POSTGRES_LINK)
            self.assertEqual(result, 'test')

    def test_get_postgres_conn_failed(self):
        mocked_connect = MagicMock()
        mocked_logger = MagicMock()
        mocked_connect.side_effect = Exception('test error')

        with patch('psycopg2.connect', mocked_connect):
            with patch.object(self.logger, 'error', mocked_logger):
                result = self.connector.get_postgres_conn()
                mocked_connect.assert_called_once_with(configuration.POSTGRES_LINK)
                self.assertEqual(result, None)
                mocked_logger.assert_called_once_with('Unable to connect to the Postgres: test error')

    def test_get_rabbit_conn_success(self):
        mocked_connect = MagicMock()
        mocked_params = MagicMock()
        mocked_connect.return_value = 'test'

        with patch('pika.BlockingConnection', mocked_connect):
            with patch('pika.ConnectionParameters', mocked_params):
                result = self.connector.get_rabbit_conn()

                mocked_params.assert_called_once_with(host=configuration.RABBIT_MQ_HOST)
                self.assertEqual(result, 'test')

    def test_get_rabbit_conn_failed(self):
        mocked_connect = MagicMock()
        mocked_params = MagicMock()
        mocked_logger = MagicMock()
        mocked_connect.side_effect = Exception('test error')

        with patch('pika.BlockingConnection', mocked_connect):
            with patch('pika.ConnectionParameters', mocked_params):
                with patch.object(self.logger, 'error', mocked_logger):
                    result = self.connector.get_rabbit_conn()
                    mocked_params.assert_called_once_with(host=configuration.RABBIT_MQ_HOST)
                    self.assertEqual(result, None)
                    mocked_logger.assert_called_once_with('Unable to connect to the Rabbit: test error')