'''
Initializes this module by setting up logging and creating the database as needed.
'''
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from .models.models import create_tables


DATA_DIR = os.path.join(os.getenv('HOME'), '.floodlight')
TARGET_FILE = os.path.join(DATA_DIR, 'scan_targets.txt')
_DB_NAME = 'floodlight.sqlite.db'
_DB_PATH = os.path.join(DATA_DIR, _DB_NAME)

_LOG_DIR = os.path.join(DATA_DIR, 'logs')
_LOG_FILE = os.path.join(_LOG_DIR, 'application.log')

_DB_CONNECTION_ENGINE = create_engine('sqlite:///' + _DB_PATH)


def initialize_db():
    '''
    Initializes the application database
    '''
    base = automap_base()
    base.prepare(_DB_CONNECTION_ENGINE)
    create_tables(_DB_CONNECTION_ENGINE)


if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

if not os.path.exists(_LOG_DIR):
    os.mkdir(_LOG_DIR)

_CREATE_LOG = not os.path.exists(_LOG_FILE)

logging.basicConfig(
    filename=_LOG_FILE,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - Process Id: %(process)d -' +
    ' %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

if _CREATE_LOG:
    logging.info('Log Created')


if not os.path.exists(_DB_PATH):
    logging.info('Database not found - creating')
    initialize_db()


def get_engine():
    return _DB_CONNECTION_ENGINE
