#!/usr/bin/python3
"""
City objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.state import State
from models.state import City


@app_views.route("/states/<state_id>/cities", strict_slashes=False)
def get_cities(state_id):
    """ Retrieves the list of all cities of a State """
    state = storage.get(State, state_id)

    if state is None:
        abort(404)

    state_cities = [city.to_dict() for city in state.cities]
    return jsonify(state_cities)


@app_views.route("/states/<state_id>/cities", methods=["POST"],
                 strict_slashes=False)
def post_city_under_state(state_id):
    state = storage.get(State, state_id)

    if state is None:
        abort(404)

    req_body = request.get_json()
    if type(req_body) is not dict:
        abort(400, "Not a JSOn")

    if "name" not in req_body:
        abort(400, "Missing name")

    req_body.update({"state_id": state_id})
    new_city = City(**req_body)
    storage.new(new_city)
    storage.save()
    return jsonify(new_city.to_dict()), 201


@app_views.route("/cities/<city_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def get_city(city_id):
    """ Retreives a City object """
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    if request.method == "GET":
        return jsonify(city.to_dict())

    if request.method == "DELETE":
        storage.delete(city)
        storage.save()
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()

        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        for key, value in req_body.items():
            if (key is not "id" and key is not "created_at" and
               key is not "updated_at"):
                setattr(city, key, value)

        storage.save()
        return jsonify(city.to_dict()), 200
