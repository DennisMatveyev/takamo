import json

from core.config import configuration


class PostgresModel:
    def __init__(self, connection):
        self.connection = connection

    def read(self):
        cur = self.connection.cursor()
        cur.execute('SELECT * from action_daemon.actions WHERE completed IS FALSE AND time_to_run <= CURRENT_TIMESTAMP ;')
        actions = cur.fetchall()
        cur.close()

        return actions


class RabbitModel:
    def __init__(self, connection, actions):
        self.connection = connection
        self.channel = self.connection.channel()
        self.actions = actions

    def send(self):
        self.channel.queue_declare(queue='task_queue')

        for action in self.actions:
            id, action_name, user_id, params, completed, success, time_to_run = action
            message = {'action': action_name,
                       'actionID': id,
                       'PLID': user_id,
                       'location': params.get('location'),
                       'numberToBuild': params.get('numberToBuild')}
            message_json = json.dumps(message)

            self.channel.basic_publish(exchange=configuration.RABBIT_EXCHANGE,
                                       routing_key=configuration.RABBIT_ROUTING_KEY,
                                       body=message_json)
