from logging import Logger, DEBUG

class LoxLoggerSingleton:
    logger = None
    params = {
        "name": "LoxLogger",
        "level": DEBUG
    }

    @classmethod
    def get_logger(cls) -> Logger:
        if cls.logger is None:
            cls.logger = Logger(**cls.params)

        return cls.logger