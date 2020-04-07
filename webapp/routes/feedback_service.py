from routes import *

import json
from flask import jsonify


@routes.route('/feedback/<uuid>', methods=['POST'])
def process_feedback(uuid):
    data = request.get_json()

    print(data)

    client = datastore.Client()

    query = client.query(kind='Route')
    route_key = client.key('Route', uuid)

    query.key_filter(route_key, '>')

    fetched_query = list(query.fetch())[0]

    route = json.loads(fetched_query['route'])

    return jsonify(route)