import json
import unittest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pika


class ActionDaemonTest(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost')
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor()
        try:
            self.cur.execute('CREATE DATABASE test_db WITH OWNER postgres;')
        except psycopg2.ProgrammingError:
            pass
        self.cur.close()
        self.conn.close()
        self.conn = psycopg2.connect(dbname='test_db', user='postgres', password='postgres', host='localhost')
        self.cur = self.conn.cursor()
        try:
            self.cur.execute(self._create_table())
        except psycopg2.ProgrammingError:
            self.conn.rollback()
            self.cur.execute('DELETE FROM actions;')

        self.cur.execute(self._fill_table())
        self.conn.commit()

        self.actions = None

        self.r_conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.r_conn.channel()

    def _create_table(self):
        create = """CREATE TABLE actions (id integer PRIMARY KEY,
                                            action_name character varying NOT NULL,
                                            user_id integer NOT NULL,
                                            parameters json,
                                            success boolean DEFAULT NULL,
                                            completed boolean NOT NULL DEFAULT false,
                                            time_to_run timestamp with time zone NOT NULL);"""
        return create

    def _fill_table(self):
        insert = """INSERT INTO actions (id, action_name, user_id, parameters, success, completed, time_to_run) VALUES
                        (1, 'go', 1, '{"key": "value"}', False, False, '2017-08-01 10:39:53.662522-05'),
                        (2, 'run', 2, '{"key": "value"}', False, False, '2017-08-01 10:49:53.662522-05'),
                        (3, 'stop', 1, '{"key": "value"}', False, False, '2017-08-01 10:42:53.662522-05');"""
        return insert

    def test_read(self):
        self.cur.execute('SELECT * from actions WHERE completed IS FALSE AND time_to_run <= CURRENT_TIMESTAMP ;')
        self.actions = self.cur.fetchall()
        self.assertEqual(len(self.actions), 3, 'Amount of actions does not equal 3.')

    def _create_actions(self):
        self.cur.execute('SELECT * from actions WHERE completed IS FALSE AND time_to_run <= CURRENT_TIMESTAMP ;')
        self.actions = self.cur.fetchall()

    def test_send(self):
        self.channel.queue_declare(queue='test')

        if self.actions == None:
            self._create_actions()

        for action in self.actions:
            id, action_name, user_id, params, completed, success, time_to_run = action
            message = {'action': action_name,
                       'actionID': id,
                       'PLID': user_id,
                       'location': params.get('location'),
                       'numberToBuild': params.get('numberToBuild')}
            message_json = json.dumps(message)

            res = self.channel.basic_publish(exchange='',
                                             routing_key='',
                                             body=message_json)

            self.assertEqual(res, True, 'Message has not been published. ')

        self.actions = None
        self.r_conn.close()

    def tearDown(self):
        self.cur.execute('DELETE FROM actions;')
        self.cur.close()
        self.conn.close()
