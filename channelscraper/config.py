import yaml


class Config:
    config = None

    @staticmethod
    def getConfig():
        """ Static access method. """
        if Config.config is None:
            Config()

        return Config.config

    def __init__(self):
        Config.config = yaml.safe_load(open("config.yaml"))
