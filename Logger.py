import logging
import logging.config
from datetime import datetime


class Logger:
    def create_logger(self, debug: bool):
        if debug:
            level = logging.DEBUG
        else:
            level = logging.WARNING

        logging.basicConfig(filename=f'./logs/capsulefarmer-{datetime.now().strftime("%Y-%m-%d")}.log', filemode="a+",
                            format='%(asctime)s %(levelname)s: %(message)s', level=level)
        log = logging.getLogger("League of Poro")
        log.info("-------------------------------------------------")
        log.info("---------------- Program started ----------------")
        log.info("-------------------------------------------------")
        return log
