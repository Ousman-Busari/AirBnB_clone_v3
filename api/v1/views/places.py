#!/usr/bin/python3
"""
City objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route("/cities/<city_id>/places", strict_slashes=False)
def get_places(city_id):
    """ Retrieves the list of all Place object uner a City Object """
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    city_places = [place.to_dict() for place in city.places]
    return jsonify(city_places)


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def post_place_under_city(city_id):
    """ Posts/creates a new Place object under a City Object """
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    req_body = request.get_json()
    if type(req_body) is not dict:
        abort(400, "Not a JSOn")

    if "user_id" not in req_body:
        abort(400, "Missing user_id")

    if storage.get(User, req_body["user_id"]) is None:
        abort(404)

    if "name" not in req_body:
        abort(400, "Missing name")

    req_body.update({"city_id": city_id})
    new_place = Place(**req_body)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route("/places/<place_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def rud_place(place_id):
    """ reads, updates, and deletes a City object """
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    if request.method == "GET":
        return jsonify(place.to_dict())

    if request.method == "DELETE":
        storage.delete(place)
        storage.save()
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()

        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        for key, value in req_body.items():
            if (key != "id" and key != "user_id" and key != "city_id" and
               key != "created_at" and key != "updated_at"):
                setattr(place, key, value)

        storage.save()
        return jsonify(place.to_dict()), 200
