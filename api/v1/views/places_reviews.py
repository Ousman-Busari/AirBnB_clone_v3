#!/usr/bin/python3
"""
Places' review objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route("/places/<place_id>/reviews", strict_slashes=False)
def get_place_reviews(place_id):
    """ Retrieves the list of all reviews of a Place """
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    places_reviews = [review.to_dict() for review in place.reviews]
    return jsonify(places_reviews)


@app_views.route("/places/<place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def post_review_under_place(place_id):
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    req_body = request.get_json()
    if type(req_body) is not dict:
        abort(400, "Not a JSOn")

    if "user_id" not in req_body:
        abort(400, "Missing user_id")

    if storage.get(User, req_body["user_id"]) is None:
        abort(404)

    if "text" not in req_body:
        abort(400, "Missing text")

    req_body.update({"place_id": place_id})
    new_review = Review(**req_body)
    storage.new(new_review)
    storage.save()
    return jsonify(new_review.to_dict()), 201


@app_views.route("/reviews/<review_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def rud_review(review_id):
    """ reads, updates, and deletes a Review object """
    review = storage.get(Review, review_id)

    if review is None:
        abort(404)

    if request.method == "GET":
        return jsonify(review.to_dict())

    if request.method == "DELETE":
        storage.delete(review)
        storage.save()
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()

        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        for key, value in req_body.items():
            if (key != "id" and key != "user_id" and key != "created_at" and
               key != "updated_at"):
                setattr(review, key, value)

        storage.save()
        return jsonify(review.to_dict()), 200
