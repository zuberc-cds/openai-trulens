import logging

class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger("common_logger")
            cls._instance.logger.setLevel(logging.INFO)
            with open('chat_logger.log', 'w'): 
                pass
            file_handler = logging.FileHandler("chat_logger.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(file_handler)
        return cls._instance