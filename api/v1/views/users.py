#!/usr/bin/python3
"""
User objects views and CRUD
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route("/users/", strict_slashes=False)
def get_users():
    """ get all User objects """
    users = storage.all(User)

    if users is None:
        abort(404)

    users_list = [user.to_dict() for user in users.values()]
    return jsonify(users_list)


@app_views.route("/users/", methods=["POST"], strict_slashes=False)
def post_user():
    """ post/create a new User Object """
    req_body = request.get_json()

    if type(req_body) is not dict:
        abort(400, "Not a JSON")

    if "email" not in req_body:
        abort(400, "Missing email")

    if "password" not in req_body:
        abort(400, "Missing password")

    new_user = User(**req_body)
    storage.new(new_user)
    storage.save()
    return jsonify(new_user.to_dict()), 201


@app_views.route("/users/<user_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def rud_user(user_id):
    """ reads, updates, and deletes an User object """
    user = storage.get(User, user_id)

    if user is None:
        abort(404)

    if request.method == "GET":
        return jsonify(user.to_dict())

    if request.method == "DELETE":
        storage.delete(user)
        storage.save()
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()

        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        for key, value in req_body.items():
            if (key != "id" and key != "created_at" and
               key != "updated_at" and key != "email"):
                print(key, value)
                setattr(user, key, value)

        storage.save()
        return jsonify(user.to_dict()), 200
