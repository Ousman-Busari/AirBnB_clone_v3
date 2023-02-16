#!/usr/bin/python3
"""
Place's amenities objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.amenity import Amenity
from os import getenv


@app_views.route("/places/<place_id>/amenities", strict_slashes=False)
def get_place_amenities(place_id):
    """ Retrieves the list of all amenities of a Place """
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    places_amenities = [review.to_dict() for review in place.amenities]
    return jsonify(places_amenities)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["POST", "DELETE"], strict_slashes=False)
def post_amenity_to_place(place_id, amenity_id):
    """ Posts an amenity object to a place object"""
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)

    if place is None or amenity is None:
        abort(404)

    if request.method == "POST":
        if amenity in place.amenities or amenity.id in place.amenity_ids:
            return jsonify(amenity.to_dict()), 200

        if getenv("HBNB_TYPE_STORAGE") == "db":
            place.amenities.append(amenity)
        else:
            place.amenity_ids.append(amenity.id)
        storage.save()
        return jsonify(amenity.to_dict()), 201

    if request.method == "DELETE":
        if amenity not in place.amenities:
            abort(404)

        if getenv("HBNB_TYPE_STORAGE") == "db":
            place.amenities.remove(amenity)
        else:
            place.amenity_ids.pop(amenity.id, None)

        storage.save()
        return jsonify({}), 200
