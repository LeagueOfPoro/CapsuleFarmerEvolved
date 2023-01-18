import logging
import logging.config
from Logger.CustomFormatter import CustomFormatter
from datetime import datetime


class Logger:
    def createLogger(self, debug: bool):
        # logging.config.dictConfig({
        #     'version': 1,
        #     'disable_existing_loggers': True,

        # })

        # log = logging.getLogger("League of Poro")
        # if (debug):
        #     log.setLevel('DEBUG')
        # else:
        #     log.setLevel('INFO')
        # ch = logging.StreamHandler()
        # if (debug):
        #     ch.setLevel('DEBUG')
        # else:
        #     ch.setLevel('INFO')
        # ch.setFormatter(CustomFormatter())
        # log.addHandler(ch)

        if (debug):
            level = logging.DEBUG
        else:
            level = logging.WARNING
        
        logging.basicConfig(filename=f'capsulefarmer-{datetime.now().strftime("%Y-%m-%d")}.log', filemode="a+", format='%(asctime)s %(message)s', level=level)
        log = logging.getLogger("League of Poro")
        log.info("-------------------------------------------------")
        log.info("---------------- Program started ----------------")
        log.info("-------------------------------------------------")
        return log
