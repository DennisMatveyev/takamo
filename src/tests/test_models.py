import unittest
import json
from unittest.mock import MagicMock

from src.models import PostgresModel, RabbitModel
from src.core.config import configuration


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
    def test_send_without_actions(self):
        actions = []
        mocked_connection = MagicMock()
        mocked_channel = MagicMock()
        mocked_connection.channel.return_value = mocked_channel
        rmq = RabbitModel(mocked_connection, actions)

        self.assertEqual(mocked_channel.basic_publish.call_count, 0)


    def test_send_with_actions(self):
        actions = [(1,2,3,{'location': 'location_one', 'numberToBuild': 'numberToBuild_one'},5,6,7),
                   (8,9,10,{'location':'location_two', 'numberToBuild':'numberToBuild_two'},12,13,14)]
        mocked_connection = MagicMock()
        mocked_channel = MagicMock()

        mocked_connection.channel.return_value = mocked_channel

        rmq = RabbitModel(mocked_connection, actions)
        rmq.send()

        first_body = {'action': 2,
                       'actionID': 1,
                       'PLID': 3,
                       'location': 'location_one',
                       'numberToBuild': 'numberToBuild_one'}
        first_publish_call = mocked_channel.basic_publish.mock_calls[0][2]
        self.assertEqual(first_publish_call['body'], json.dumps(first_body))
        self.assertEqual(first_publish_call['exchange'], configuration.RABBIT_EXCHANGE)
        self.assertEqual(first_publish_call['routing_key'], configuration.RABBIT_ROUTING_KEY)

        sec_body = {'action': 9,
                       'actionID': 8,
                       'PLID': 10,
                       'location': 'location_two',
                       'numberToBuild': 'numberToBuild_two'}

        sec_publish_call = mocked_channel.basic_publish.mock_calls[1][2]
        self.assertEqual(sec_publish_call['body'], json.dumps(sec_body))
        self.assertEqual(sec_publish_call['exchange'], configuration.RABBIT_EXCHANGE)
        self.assertEqual(sec_publish_call['routing_key'], configuration.RABBIT_ROUTING_KEY)


        self.assertEqual(mocked_channel.basic_publish.call_count, 2)
