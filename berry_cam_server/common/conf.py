import os
import secrets

import yaml


class Config:
    """
    This class handles all configuration related implementation.
    It will read server and user config from given config file and will handle also api key updates.
    """

    # The config file to parse. Public so that it can be overwritten e.g. for testing purpose.
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'conf.yaml')

    @staticmethod
    def get_user_config(username):
        """
        Returns the user configuration for a given user from the yaml file.
        None if user does not exist.

        :param str username: The user to get the configuration for.
        :return: The user configuration or None.
        :rtype: dict
        """
        with open(Config.config_file) as config_file:
            config = yaml.safe_load(config_file)

            if username in config["user"]:
                return config["user"][username]

            return None

    @staticmethod
    def get_server_config():
        """
        Returns the server configuration from the yaml file.
        :return: The server configuration.
        :rtype: dict
        """
        with open(Config.config_file) as config_file:
            config = yaml.safe_load(config_file)
            server_config = {}
            for key in config["server"]:
                server_config[key.upper()] = config["server"][key]

            return server_config

    @staticmethod
    def update_api_key(username):
        """
        Updates the api key for a given username.

        :param username: The username for which the api key should be updated.
        :return: The new api key
        :rtype: str
        """
        with open(Config.config_file, 'r') as config_file:
            config = yaml.safe_load(config_file)

        with open(Config.config_file, 'w') as config_file:
            new_key = secrets.token_hex(nbytes=16)
            config["user"][username]["api_key"] = new_key
            yaml.safe_dump(config, config_file)
            return new_key

    @staticmethod
    def get_api_keys():
        """
        Returns a set of all valid api keys. Might be empty

        :return: A set of all api keys
        :rtype: set
        """
        api_keys = set()
        with open(Config.config_file, 'r') as config_file:
            config = yaml.safe_load(config_file)
            for user in config["user"]:
                api_keys.add(config["user"][user]["api_key"])

        return api_keys
