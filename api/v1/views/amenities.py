#!/usr/bin/python3
"""
amenities object views and CRUD
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.amenity import Amenity


@app_views.route("/amenities/", strict_slashes=False)
def get_amenities():
    """ get all Amenity objects """
    amenities = storage.all(Amenity)

    if amenities is None:
        abort(404)

    amenities_list = [amenity.to_dict() for amenity in amenities.values()]
    return jsonify(amenities_list)


@app_views.route("/amenities/", methods=["POST"], strict_slashes=False)
def post_amenity():
    """ post/create a new Amenity Object """
    req_body = request.get_json()

    if type(req_body) is not dict:
        abort(400, "Not a JSON")

    if "name" not in req_body:
        abort(400, "Missing name")

    new_amenity = Amenity(**req_body)
    storage.new(new_amenity)
    storage.save()
    return jsonify(new_amenity.to_dict()), 201


@app_views.route("/amenities/<amenity_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def rud_amenity(amenity_id):
    """ reads, updates, and deletes an Amenity object """
    amenity = storage.get(Amenity, amenity_id)

    if amenity is None:
        abort(404)

    if request.method == "GET":
        return jsonify(amenity.to_dict())

    if request.method == "DELETE":
        storage.delete(amenity)
        storage.save()
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()

        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        if "name" not in req_body:
            abort(400, "Missing name")

        for key, value in req_body.items():
            if (key is not "id" and key is not "created_at" and
               key is not "updated_at"):
                setattr(amenity, key, value)

        storage.save()
        return jsonify(amenity.to_dict()), 200
