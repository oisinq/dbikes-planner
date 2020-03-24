from routes import *
from flask import Flask

app = Flask(__name__)
app.register_blueprint(routes)
app.run()