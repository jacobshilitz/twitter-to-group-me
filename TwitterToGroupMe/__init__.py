from flask import Flask, request

import logging.config
import yaml

with open('logging.yaml', 'r') as f:
    log_cfg = yaml.safe_load(f.read())

    logging.config.dictConfig(log_cfg)
    log = logging.getLogger(__name__)

# log = logging.getLogger()
log.info('starting..')

app = Flask(__name__)

import TwitterToGroupMe.views
