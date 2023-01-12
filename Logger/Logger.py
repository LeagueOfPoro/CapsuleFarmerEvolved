import logging
import logging.config
from Logger.CustomFormatter import CustomFormatter


class Logger:
    def createLogger(self, debug: bool):
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })

        log = logging.getLogger("League of Poro")
        if (debug):
            log.setLevel('DEBUG')
        else:
            log.setLevel('INFO')
        ch = logging.StreamHandler()
        if (debug):
            ch.setLevel('DEBUG')
        else:
            ch.setLevel('INFO')
        ch.setFormatter(CustomFormatter())
        log.addHandler(ch)

        return log
