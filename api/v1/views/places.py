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

    combined_cities_unique_ids = []
    if "states" in req_body and len(req_body.get("states")) != 0:
        states_ids_list = req_body.get("states")

        all_cities = list(storage.all(City).values())
        states_cities_ids = [city.id for city in all_cities if city.state_id in states_ids_list]
        combined_cities_unique_ids += states_cities_ids

    if "cities" in req_body and len(req_body["cities"]) != 0:
        cities_ids_list = req_body["cities"]
        combined_cities_unique_ids += cities_ids_list
        print(combined_cities_unique_ids)

        for city_id in cities_ids_list:
            if city_id not in combined_cities_unique_ids:
                combined_cities_unique_ids.append(city_id)

        cities_list = [storage.get(City, city_id)
                       for city_id in combined_cities_unique_ids]

    if len(combined_cities_unique_ids) == 0:
        all_places = list(storage.all(Place).values())
    else:
        all_places = []
        for city_id in combined_cities_unique_ids:
            city = storage.get(City, city_id)
            all_places += city.places

    if "amenities" in req_body and len(req_body.get("amenities")) != 0:
        amenities_ids_list = req_body["amenities"]

        filtered_places = []
        for place in all_places:
            place_amenities_ids = [amenity.id for amenity in
                                   place.amenities]
            if (all(elem in place_amenities_ids for elem in
               amenities_ids_list)):
                filtered_places.append(place)

        filtered_places_list = [place.to_dict() for place in filtered_places]
    else:
        filtered_places_list = [place.to_dict() for place in all_places]

    return jsonify(filtered_places_list), 201
