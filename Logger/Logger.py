import logging
import logging.config

from Logger.CustomFormatter import CustomFormatter

class Logger:
    def createLogger(self):
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })

        log = logging.getLogger("League of Poro")
        log.setLevel('DEBUG')
        ch = logging.StreamHandler()
        ch.setLevel('DEBUG')
        ch.setFormatter(CustomFormatter())
        log.addHandler(ch)

        return log
