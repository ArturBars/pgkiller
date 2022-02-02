import logging
import os


def check_dir(path):
    """Check dir. Create if not exists."""
    if not os.path.isdir(path):
        os.makedirs(path)
        return True
    return False


check_dir('logs')

fileHandler = logging.FileHandler('logs/pgkiller.log')
consoleHandler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        fileHandler,
        consoleHandler
    ]
)
logger = logging.getLogger()

APPS = {
    "app-name": {
        "host": "localhost",
        "database": "public",
        "user": "postgres",
        "port": 5432,
        "password": "postgres"
    }
}

LIMIT_CONNECTIONS = 15

DELAY = 30  # seconds

CONNECTION_ATTEMPTS = 5
