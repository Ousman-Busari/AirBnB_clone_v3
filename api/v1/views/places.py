#!/usr/bin/python3
"""
Place objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity
from os import getenv
from sqlalchemy.orm import relationship


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


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """ retrieves all Place objects depending
    of the JSON in the body of the request """
    req_body = request.get_json()
    if type(req_body) is not dict:
        abort(400, "Not a JSOn")

    all_places = list(storage.all(Place).values())

    if "states" in req_body and len(req_body.get("states")) != 0:
        states_ids = req_body.get("states")

        all_cities = list(storage.all(City).values())
        states_cities = set([city.id for city in all_cities if city.state_id in states_ids])
    else:
        states_cities = set()

    if "cities" in req_body and len(req_body.get("cities")) != 0:
        req_cities_ids = req_body.get("cities")

        cities_ids = set([
            city_id for city_id in req_cities_ids if storage.get(City, city_id)
        ])
        states_cities = states_cities.union(cities_ids)

    if len(states_cities) > 0:
        all_places = [place for place in all_places if place.city_id in states_cities]

    filtered_places =[]
    if "amenities" in req_body and len(req_body.get("amenities")) != 0:
        req_amenities_ids = req_body.get("amenities")

        amenities_ids = set([
            amenity_id for amenity_id in req_amenities_ids if storage.get(Amenity, amenity_id)
        ])
        for place in all_places:
            place_amenities_ids = None
            if getenv('HBNB_TYPE_STORAGE') == "db":
                place_amenities_ids = [amenity.id for amenity in place.amenities]
            elif len(place.amenities) > 0:
                place_amenities_ids = place.amenities

            if place_amenities_ids and all(elem in place_amenities_ids for elem in
               amenities_ids):
                filtered_places.append(place)

        filtered_places = [place.to_dict() for place in filtered_places]
    else:
        filtered_places = [place.to_dict() for place in all_places]

    return jsonify(filtered_places)
