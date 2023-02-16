#!/usr/bin/python3
"""
State objects view implementation
"""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.state import State
import json


@app_views.route("/states", strict_slashes=False)
def get_states():
    """ Retrives all state object from the storage"""
    all_states_in_list = list(storage.all(State).values())
    list_all_states_obj = [
        state.to_dict() for state in all_states_in_list
    ]
    return jsonify(list_all_states_obj)


@app_views.route("/states", methods=["POST"], strict_slashes=False)
def post_state():
    """ Creates and add a new state object to the storage """
    req_body = request.get_json()
    if type(req_body) is not dict:
        abort(400, "Not a JSON")

    if "name" not in req_body:
        abort(400, "Missing name")

    new_state = State(**req_body)
    storage.new(new_state)
    storage.save()
    return jsonify(new_state.to_dict()), 201


@app_views.route("/states/<state_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def state_action(state_id):
    """ retreives and manipulate a State object """
    state = storage.get(State, state_id)
    if state is None:
        abort(404)

    if request.method == "GET":
        return jsonify(state.to_dict())

    if request.method == "DELETE":
        storage.delete(state)
        return jsonify({}), 200

    if request.method == "PUT":
        req_body = request.get_json()
        if type(req_body) is not dict:
            abort(400, "Not a JSON")

        for key, value in req_body.items():
            if (key is not "id" and key is not "created_at" and
               key is not "updated_at"):
                setattr(state, key, value)
        storage.save()
        return jsonify(state.to_dict())
