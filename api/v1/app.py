#!/usr/bin/python3
"""
API setup with flask
"""
from flask import Flask, make_response, jsonify
from models import storage
from api.v1.views import app_views
from os import getenv


app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def close_app(exception):
    """ closes the app and all connections """
    storage.close()


@app.errorhandler(404)
def page_not_found(err):
    """ returns a json as a 404 response """
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    HOST = getenv("HBNB_API_HOST", "0.0.0.0")
    PORT = getenv("HBNB_API_PORT", "5000")
    app.run(host=HOST, port=PORT, threaded=True)
