from . import routes

from flask import request
from google.cloud import datastore


@routes.route('/feedback/<uuid>', methods=['POST'])
def process_feedback(uuid):
    data = request.get_json()

    print(data)

    client = datastore.Client()

    feedback_key = client.key('Feedback', uuid)

    route = datastore.Entity(key=feedback_key, exclude_from_indexes=['Feedback'])
    route.update({"route": data})

    client.put(route)

    return '', 204
