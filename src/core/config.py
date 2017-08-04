import json
import os
# from json import JSONDecodeError

from .logger import Logger


class MetaConfiguration(type):
    ENVIRON_CONFIG_PATH = '../settings.json'  # default config path
    instance = None  # lonely single instance

    def __call__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(MetaConfiguration, cls).__call__(*args, **kwargs)
            config_path = os.environ.get('ENVIRON_CONFIG_PATH', cls.ENVIRON_CONFIG_PATH)
            cls.update_fields_from_config(cls.instance, config_path)
        return cls.instance

    @staticmethod
    def update_fields_from_config(instance, config_path):
        """
        Update fields from config file by its filepath.
        :param instance:
        :param config_path:
        :return:
        """
        try:
            config = open(config_path).read()
            config_obj = json.loads(config)
            for field in config_obj:
                setattr(instance, field, config_obj[field])
        except FileNotFoundError as err:
            Logger.get_logger().warn("Config file hadn't been found at `%s` path" % config_path)
        # except JSONDecodeError as err:
        #     Logger.get_logger().warn("Config parse error at `%s` path" % config_path)
        return instance


class Configuration(metaclass=MetaConfiguration):
    """
    Main configuration class. True Singleton.
    It knows about all necessary credentials and opts.
    """
    RABBIT_MQ_HOST = 'localhost'
    RABBIT_EXCHANGE = ''
    RABBIT_ROUTING_KEY = 'orchestrator'
    POSTGRES_LINK = "postgresql://productioncenter:productioncenter@127.0.0.1:5432/productioncenter"
    LOG_FILE = "./action_daemon_logfile.log"
    DEBUG = True


configuration = Configuration()
