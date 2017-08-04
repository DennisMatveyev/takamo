import unittest
from unittest.mock import MagicMock

from src.models import PostgresModel


class TestPostgresModel(unittest.TestCase):
    def test_read(self):
        expected_text = 'SELECT * from action_daemon.actions WHERE completed IS FALSE AND time_to_run <= CURRENT_TIMESTAMP ;'

        mocked_connection = MagicMock()
        mocked_cursor = MagicMock()
        mocked_connection.cursor.return_value = mocked_cursor
        mocked_cursor.fetchall.return_value = 'test'

        pm = PostgresModel(connection=mocked_connection)
        result = pm.read()
        self.assertEqual(result, 'test')

        mocked_connection.cursor.assert_called_once_with()
        mocked_cursor.close.assert_called_once_with()
        mocked_cursor.fetchall.assert_called_once_with()
        mocked_cursor.execute.assert_called_once_with(expected_text)


class TestRabbitModel(unittest.TestCase):
    def test_send(self):
        pass
