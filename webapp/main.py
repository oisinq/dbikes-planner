from routes import *
from flask import Flask


app = Flask(__name__)
app.register_blueprint(routes)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    # app = Flask(__name__)
    # app.register_blueprint(routes)
    app.run(host='127.0.0.1', debug=True, threaded=True)
