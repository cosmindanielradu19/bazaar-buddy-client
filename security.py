import random
import string
import setproctitle
from configuration import Configuration
from logging import Logger

RANDOM_GLOBAL_VALUE = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(12, 16)))


class Security:
    def __init__(self, configuration: Configuration, logger: Logger):
        self.configuration = configuration
        self.logger = logger

    def randomize_process_name(self):
        """
        used to ensure the process name is not easily identifiable
        """

        self.logger.info(f"Randomizing process name to {RANDOM_GLOBAL_VALUE}")
        setproctitle.setproctitle(RANDOM_GLOBAL_VALUE)
        return
