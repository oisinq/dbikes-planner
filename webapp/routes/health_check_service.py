from . import routes

from flask import request
from google.cloud import datastore


@routes.route('/health-check')
def health_check():
    return 'OK!'
