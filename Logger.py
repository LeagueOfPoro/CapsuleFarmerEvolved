import logging
import logging.config
from datetime import datetime


class Logger:
    def createLogger(self, debug: bool):
        level = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(filename=f'./logs/capsulefarmer-{datetime.now().strftime("%Y-%m-%d")}.log', filemode="a+",
                            format='%(asctime)s %(levelname)s: %(message)s', level=level)
        log = logging.getLogger("League of Poro")
        log.info("-------------------------------------------------")
        log.info("---------------- Program started ----------------")
        log.info("-------------------------------------------------")
        return log
