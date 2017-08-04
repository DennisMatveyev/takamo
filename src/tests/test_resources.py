import unittest
from unittest.mock import MagicMock, patch

from core.config import configuration
from resources import Connector


class TestConnector(unittest.TestCase):
    def test_get_postgres_conn_success(self):
        connector = Connector()
        mocked_connect = MagicMock()
        mocked_connect.return_value = 'test'

        with patch('psycopg2.connect', mocked_connect):
            result = connector.get_postgres_conn()
            mocked_connect.assert_called_once_with(configuration.POSTGRES_LINK)
            self.assertEqual(result, 'test')

    def test_get_postgres_conn_failed(self):
        connector = Connector()
        mocked_connect = MagicMock()
        mocked_connect.side_effect = Exception('test error')

        with patch('psycopg2.connect', mocked_connect):
            result = connector.get_postgres_conn()
            mocked_connect.assert_called_once_with(configuration.POSTGRES_LINK)
            self.assertEqual(result, None)

    def test_get_rabbit_conn_success(self):
        connector = Connector()

        pass

    def test_get_rabbit_conn_failed(self):
        connector = Connector()

        pass
